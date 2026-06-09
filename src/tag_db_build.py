"""Build the local lookup DB: items + a unique-token table that resolves ANY scanned
token to exactly one item (the "bucket" model).

Invariant: a token belongs to exactly one item. The tokens.token PRIMARY KEY enforces
it physically; violations in the source data are resolved to a deterministic winner and
written to a conflict report for cleanup in DMSi.

Run:  python -m src.tag_db_build
Degrades gracefully: with only data/xref.xlsx present it still builds the tokens table
(items will lack descriptions/prices until the DMSi export has run).
"""
import json
import os
import re
import sqlite3
from datetime import date

import pandas as pd

from . import config

UPC_RE = re.compile(r"^\d{12,13}$")
SCI_RE = re.compile(r"^\d(\.\d+)?[eE]\+?\d+$")


def _is_junk(tok):
    return tok == "" or set(tok) == {"0"} or SCI_RE.match(tok) is not None


def _clean(v):
    if v is None:
        return ""
    return str(v).strip()


def build(cfg=None):
    cfg = cfg or config.load()
    xref_path = config.root_path(cfg["files"]["xref"])
    inv_json = config.root_path(cfg["files"]["inventory_json"])
    inv_xlsx = config.root_path(cfg["files"]["inventory_xlsx"])
    db_path = config.root_path(cfg["db"]["path"])
    report_dir = config.root_path(cfg["db"]["conflict_report_dir"])

    items = _load_items(inv_json, inv_xlsx)
    print(f"items from DMSi export: {len(items)}")

    pairs, primary_upc = _gather_tokens(xref_path, items)
    print(f"distinct (token,item) pairs after clean+collapse: {len(pairs)}")

    # ensure every item referenced by a token exists in items
    for _, item_code in pairs:
        items.setdefault(item_code, _blank_item(item_code))
    for ic, upc in primary_upc.items():
        if ic in items:
            items[ic]["primary_upc"] = upc

    resolved, conflicts = _resolve(pairs, items, primary_upc)
    print(f"unique tokens written: {len(resolved)}")
    print(f"one-bucket violations:  {len(conflicts)} tokens")

    _write_db(db_path, items, resolved)
    report = _write_conflicts(report_dir, conflicts, items)
    if report:
        print(f"conflict report: {report}")
    print(f"DB written: {db_path}")
    return {"items": len(items), "tokens": len(resolved), "conflicts": len(conflicts)}


# --------------------------------------------------------------------------
def _blank_item(item_code):
    return {
        "item_code": item_code, "description": "", "extended_desc": "",
        "part_number": "", "size": "", "selling_uom": "", "cached_price": None,
        "primary_upc": "", "default_location": "", "on_hand": None,
        "available": None,
    }


def _get(row, *names):
    for n in names:
        if n in row and row[n] not in (None, ""):
            return row[n]
    return ""


def _load_items(inv_json, inv_xlsx):
    items = {}
    if os.path.exists(inv_json):
        with open(inv_json, "r", encoding="utf-8") as f:
            rows = json.load(f)
        for r in rows:
            ic = _clean(_get(r, "ItemCode", "Item"))
            if not ic:
                continue
            items[ic] = {
                "item_code": ic,
                "description": _clean(_get(r, "Description", "ItemDescription")),
                "extended_desc": _clean(_get(r, "ExtendedDescription")),
                "part_number": _clean(_get(r, "PartNumber", "Part")),
                "size": _clean(_get(r, "Size")),
                "selling_uom": _clean(_get(r, "UOM", "SellingUOM", "StockingUOM")),
                "cached_price": _num(_get(r, "GrossPrice", "Price")),
                "primary_upc": _clean(_get(r, "UPC")),
                "default_location": _clean(_get(r, "Location", "DefaultLocation")),
                "on_hand": _num(_get(r, "OnHand", "QuantityOnHand")),
                "available": _num(_get(r, "Available", "QuantityAvailable")),
            }
    else:
        print(f"  (no {os.path.basename(inv_json)} yet — run src.dmsi_inventory_export "
              "to populate descriptions/prices)")

    if os.path.exists(inv_xlsx):
        df = pd.read_excel(inv_xlsx, dtype=str)
        df.columns = df.columns.str.strip()
        ic_col = _pick(df, ["Item", "ItemCode", "Item Code"])
        upc_col = _pick(df, ["UPC", "Upc"])
        loc_col = _pick(df, ["Location", "Default Location"])
        for _, row in df.iterrows():
            ic = _clean(row.get(ic_col))
            if not ic:
                continue
            it = items.setdefault(ic, _blank_item(ic))
            if upc_col and _clean(row.get(upc_col)):
                it["primary_upc"] = _clean(row.get(upc_col))
            if loc_col and _clean(row.get(loc_col)):
                it["default_location"] = _clean(row.get(loc_col))
    return items


def _gather_tokens(xref_path, items):
    """Return (set of (token,item) pairs, dict item->primary_upc)."""
    pairs = set()
    primary_upc = {}

    df = pd.read_excel(xref_path, dtype=str)
    df.columns = df.columns.str.strip()
    tok_col = _pick(df, ["xref-num", "xref", "Xref", "Token"])
    item_col = _pick(df, ["Item", "ItemCode"])
    for tok, item in zip(df[tok_col], df[item_col]):
        tok = _clean(tok)
        item = _clean(item)
        if not tok or not item or _is_junk(tok):
            continue
        pairs.add((tok, item))

    # every item code is itself a scannable token (covers items seen only in xref)
    for ic in {item for _, item in pairs}:
        if ic and not _is_junk(ic):
            pairs.add((ic, ic))

    # authoritative UPC is also a token; record it as the item's primary
    for ic, it in items.items():
        upc = _clean(it.get("primary_upc"))
        if upc and not _is_junk(upc):
            pairs.add((upc, ic))
            primary_upc[ic] = upc
        if ic and not _is_junk(ic):
            pairs.add((ic, ic))
    return pairs, primary_upc


def _resolve(pairs, items, primary_upc):
    """One token -> one item. Returns (resolved {token:(item,source)}, conflicts {token:[items]})."""
    by_token = {}
    for tok, item in pairs:
        by_token.setdefault(tok, set()).add(item)

    resolved = {}
    conflicts = {}
    item_codes = set(items.keys())
    for tok, candidates in by_token.items():
        if len(candidates) == 1:
            ic = next(iter(candidates))
            resolved[tok] = (ic, _source(tok, ic, primary_upc))
            continue
        conflicts[tok] = sorted(candidates)
        winner = _pick_winner(tok, candidates, items, primary_upc, item_codes)
        resolved[tok] = (winner, _source(tok, winner, primary_upc))
    return resolved, conflicts


def _pick_winner(tok, candidates, items, primary_upc, item_codes):
    if tok in candidates and tok in item_codes:
        return tok                                   # token is an item's own code
    upc_owners = [c for c in candidates if primary_upc.get(c) == tok]
    if len(upc_owners) == 1:
        return upc_owners[0]                          # authoritative UPC match
    in_stock = [c for c in candidates if (items.get(c, {}).get("available") or 0) > 0]
    if len(in_stock) == 1:
        return in_stock[0]
    return sorted(candidates)[0]                      # stable, logged in report


def _source(tok, ic, primary_upc):
    if tok == ic:
        return "item_code"
    if primary_upc.get(ic) == tok:
        return "xlsx_upc"
    return "xref"


def _write_db(db_path, items, resolved):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError as e:
            raise SystemExit(f"Cannot overwrite {db_path} (is it open in another app?): {e}")
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE items (
          item_code TEXT PRIMARY KEY, description TEXT, extended_desc TEXT,
          part_number TEXT, size TEXT, selling_uom TEXT, cached_price REAL,
          primary_upc TEXT, default_location TEXT, on_hand REAL, available REAL,
          updated_at TEXT
        );
        CREATE TABLE tokens (
          token TEXT PRIMARY KEY, item_code TEXT NOT NULL, source TEXT
        );
        CREATE INDEX idx_tokens_item ON tokens(item_code);
        """
    )
    today = date.today().isoformat()
    cur.executemany(
        "INSERT INTO items VALUES (:item_code,:description,:extended_desc,:part_number,"
        ":size,:selling_uom,:cached_price,:primary_upc,:default_location,:on_hand,"
        ":available,:updated_at)",
        [dict(it, updated_at=today) for it in items.values()],
    )
    cur.executemany(
        "INSERT OR IGNORE INTO tokens (token,item_code,source) VALUES (?,?,?)",
        [(t, ic, src) for t, (ic, src) in resolved.items()],
    )
    con.commit()
    con.close()


def _write_conflicts(report_dir, conflicts, items):
    if not conflicts:
        return None
    os.makedirs(report_dir, exist_ok=True)
    rows = []
    for tok, cands in sorted(conflicts.items()):
        for ic in cands:
            it = items.get(ic, {})
            rows.append({
                "token": tok, "item_code": ic,
                "description": it.get("description", ""),
                "primary_upc": it.get("primary_upc", ""),
                "available": it.get("available"),
            })
    path = os.path.join(report_dir, f"token_conflicts_{date.today().isoformat()}.xlsx")
    pd.DataFrame(rows).to_excel(path, index=False)
    return path


def _pick(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    build()

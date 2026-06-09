# HIO Bin-Tag App — Project Brief

A BarTender replacement for Home Improvement Outlet: a responsive web app that
resolves a scanned token to an item, fetches the **live** DMSi Agility price, and
prints a price/bin tag to either a wearable **Zebra ZQ620 Plus** (thermal, ZPL) or a
**Centurion UN OR4P** 32-up laser sheet (PDF). Used on the floor from a phone and at
a desk for batch runs.

This document is the build spec and the hand-off file for Claude Code. Treat it as
the source of truth; flag any conflict rather than guessing.

---

## 1. Goals and non-goals

**Goals**
- One UI, responsive, mobile-first. Phone = walk the aisle, scan, see live price, print one thermal tag. Desktop = same lookup plus batch sheet runs.
- Live price at print time (no stale snapshot on the shelf).
- Replace BarTender entirely: no SQL-logging latency, no license, full layout control.
- Two output renderers from one data core and one field set.

**Non-goals (explicitly out of scope)**
- **No price write-back to DMSi.** This is reprint-to-match only: prices change
  upstream (Orgill updater, DMSi pricing admin); the floor walk reprints tags so the
  shelf catches up. DMSi's public API has no clean retail-price-set endpoint anyway
  (Pricing service is read-only; only `ItemUpdate`/`InventoryCostUpdate` write, and
  neither is a safe per-item shelf-price operation).
- No new BarTender-style visual designer. Layouts are config/code.

---

## 2. Architecture

```
Phone / Desktop browser
        |  HTTPS
        v
   Flask backend  (Windows box with line-of-sight to DMSi + both printers)
   ├── persistent DMSi session (Login + refresh)
   ├── local SQLite "bucket" DB  (token -> item resolution + cached fields)
   ├── live price calls to DMSi  (ItemPriceAndAvailabilityList, customer 1)
   ├── ZPL renderer   -> RAW spool to shared ZQ620
   └── PDF renderer    -> laser printer (OR4P sheet)
```

The backend is the **print broker**. A phone browser cannot open a raw socket to a
printer, so *every* print routes phone -> Flask -> printer. The wearable Zebra works
from the floor as long as the Flask host can reach its shared queue (or its IP:9100).

Suggested stack: Python 3.11+, Flask, `requests` (DMSi), `reportlab` (PDF + Code 128),
`pywin32` (RAW spool on Windows). Frontend: vanilla HTML/CSS/JS + a camera-scan lib
(ZXing-js or html5-qrcode). No heavy framework needed.

---

## 3. Data layer — the bucket DB

Rebuilt on a schedule by `tag_db_build.py` (evolved from the old bartender export, which is being retired). Resolves *any*
scanned token to exactly one item; carries descriptive fields + a cached price for
offline/fallback.

### Invariant (confirmed with the user)
An item is a **bucket**. A token (UPC, vendor SKU, legacy code, the item code
itself) belongs to **exactly one** bucket. One item -> many tokens is fine; the same
(token, item) repeated is fine (collapses); one token -> two items is a **violation**
to be reported and cleaned, never designed around.

### Schema
```sql
CREATE TABLE items (
  item_code      TEXT PRIMARY KEY,
  description     TEXT,   -- ItemDescription
  extended_desc   TEXT,   -- ExtendedDescription
  part_number     TEXT,   -- PartNumber (may be blank)
  size            TEXT,
  selling_uom     TEXT,   -- e.g. EA
  cached_price    REAL,   -- last known GrossPrice/cash price (fallback only)
  primary_upc     TEXT,   -- authoritative xlsx UPC (sheet/batch barcode source)
  default_location TEXT,
  on_hand         REAL,
  available       REAL,
  updated_at      TEXT
);

CREATE TABLE tokens (
  token      TEXT PRIMARY KEY,   -- the PK *physically* enforces one-bucket
  item_code  TEXT NOT NULL REFERENCES items(item_code),
  source     TEXT                -- 'xref' | 'xlsx_upc' | 'item_code'
);
CREATE INDEX idx_tokens_item ON tokens(item_code);
```

### Build pipeline
1. Pull item scope from DMSi (existing `dmsi_inventory_export.run_export()`), enrich
   from `inventory_export.xlsx`.
2. Gather tokens from: all `xref.xlsx` values + authoritative xlsx UPC + the item code.
3. Clean: strip; drop blanks, all-zero junk (`000000000000`), and scientific-notation
   garbage (`8.85911E+11` — unrepairable, see below).
4. Collapse exact (token, item) duplicates.
5. Detect violations (token -> >1 item). Resolve a deterministic winner for the live
   `tokens` row; write **all** conflicts to `token_conflicts_<date>.xlsx` for cleanup.
   Winner rule: token == an item code -> that item; else authoritative-UPC match beats
   xref-only; else prefer in-stock/available; else lowest item_code (logged).

### Known data scope (measured from current xref.xlsx, 210,416 rows)
- 145,295 distinct tokens; **16,041 (11%) violate one-bucket** (16,036 genuine, ~8,228
  items entangled; almost all 2-bucket). These are the cleanup punch-list.
- 48,618 rows are exact (token,item) repeats (harmless).
- 21 scientific-notation tokens (e.g. `8.85911E+11` covering 127 items) are **upstream
  corruption** — the xref export coerced the UPC column to a number and destroyed the
  digits. FIX AT SOURCE: export the UPC column as text. The app cannot recover these.

---

## 4. DMSi Agility integration (read-only)

- Base (prod): `https://api-1634-1.dmsi.com/.../AgilityPublic/rest` — Branch `01HIO`,
  user `HIOAPI`, house CustomerID `1`. Headers: `ContextId`, `Branch`, `Content-Type`.
- **Login** -> `ContextId` (idle timeout default 4h, up to 24h). Keep one persistent
  session; refresh on 401/expiry. Never Login per request.
- **Live price + availability:** `Inventory/ItemPriceAndAvailabilityList`
  - `dtPriceAndAvailRequest`: `CustomerID:"1"`, `ShiptoSequence:1`, `SaleType:""`,
    `DateToCalculatePriceFor:""` (today), `UseOrderRestrictions:true`
  - `dtItemToProcessRequest`: `ItemCode:<resolved>`, `OrderQuantity:1`, `UOM:<selling>`
  - Returns the computed **cash-sale** price for customer 1 (correct shelf price) and
    quantities. **Always inspect `ItemAuditResults`** even on success — a mispriced tag
    must never print silently. Batch: this method takes a list, so one call per sheet.
- **Descriptive fields** (if not already cached in items): `Inventory/ItemsList` /
  `ItemsInChunksList` with `IncludePriceData=true`.
- Payload convention: `request -> ds<Name> -> dt<Name> -> [ {fields} ]`, casing-sensitive.
- Full endpoint reference lives in `DMSi_Agility_API_v619_reference.md` (192 endpoints).

---

## 5. Renderers

Both consume the same resolved record and the same field set. Layout differs per media.

### 5a. Thermal — Zebra ZQ620 Plus (ZPL)
- 203 dpi. Media 2.83" x 2.00" -> **canvas 574 x 406 dots** (`^PW574`, `^LL406`).
- Printer only burns dark; the yellow is pre-printed media.
- **Barcode value = the scanned token** (round-trip; reprint carries the same number).
- Symbology: **Code 128**.
- Send: RAW via Windows spooler (`pywin32` `StartDocPrinter` datatype `"RAW"` ->
  `WritePrinter`) to the shared queue, or raw TCP `:9100` to the printer IP.

Field layout (dots from top-left, `^FO x,y`):

| Field | x,y | font h | justify | source |
|---|---|---|---|---|
| Description | 20,14 | 40 | left, wrap 2 lines, clip | Description + " " + ExtendedDesc |
| Part # | 20,206 | 30 | left | PartNumber, fallback ItemCode if blank |
| Item code | 20,248 | 30 | left | ItemCode |
| Price | 552,116 | 80 | right | live price (cust 1) |
| UOM | 552,256 | 34 | right | selling UOM |
| Human number | 287,300 | 26 | center | scanned token |
| Barcode (Code 128) | ~58,336 | 60 tall | center | scanned token |

Two inches is tight; these are conservative starting sizes — tune on first test print.

### 5b. Sheet — Centurion UN OR4P (PDF, reportlab)
- US Letter 8.5 x 11, **4 cols x 8 rows = 32 labels**.
- Per measurement of the actual sheet: label **2.0625" W x 1.25" H**, side margins
  ~0.125", top/bottom ~0.5", near-zero gutters. Yellow highlight ~0.65" tall at one
  end of each cell; ~0.6" white strip for the barcode.
- **Barcode value = authoritative UPC** (item-code fallback) — batch has no scan.
- Symbology: **Code 128** (reportlab `code128`).
- Geometry in **config**, not hardcoded. Ship a **calibration mode** that prints cell
  outlines + crosshairs so the user nudges offsets once and locks them. This also
  resolves the 180°/feed-orientation ambiguity (header + arrows) found in the scan.
- **Partial-sheet support:** start at cell N (1-32) to use leftover sheets.
- Re-proportioned layout for the smaller label (compact description, price over the
  yellow, Code 128 in the white strip) — produce a proof before finalizing.

---

## 6. UI flows

One responsive app served by Flask. Mobile-first.

### Mobile (floor)
1. Big scan field. Input: **camera** (ZXing decoding Code 128/UPC), **Bluetooth wedge**
   scanner (types token + Enter), or manual entry.
2. On token: resolve -> show item description, item/part, **live price** large, UOM,
   on-hand. If token unresolved -> clear "not found" + manual item entry.
3. **[Print tag]** -> thermal ZPL -> RAW spool to the worn ZQ620.
4. (Optional) recent-prints list for quick reprints.

### Desktop (batch)
- Same single lookup + print.
- **Batch builder:** add items by **paste/import a list** AND **scan-to-queue** (both).
  Resolve + one live-price call for the queue. Choose start cell. Preview the 32-up
  sheet. Generate PDF -> laser printer.

---

## 7. Endpoints (Flask)

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | responsive app shell |
| GET | `/api/resolve?token=` | token -> item + live price (+ audit check) |
| POST | `/api/print/thermal` | body: token -> ZPL -> RAW spool |
| POST | `/api/batch/resolve` | list of tokens/items -> resolved rows + prices |
| POST | `/api/print/sheet` | rows + start_cell -> OR4P PDF -> laser print |
| GET | `/api/sheet/preview` | render PDF for on-screen preview |
| GET | `/api/calibrate/sheet` | calibration grid PDF |
| GET | `/api/health` | DMSi session + printer reachability |

---

## 8. Config (example `config.json`)

```json
{
  "dmsi": { "base_url": "", "branch": "01HIO", "user": "HIOAPI", "customer_id": "1" },
  "db": { "path": "hio_items.db" },
  "thermal": { "printer_share": "\\\\HOST\\ZQ620", "dpi": 203, "pw": 574, "ll": 406 },
  "sheet": {
    "page": "letter", "cols": 4, "rows": 8,
    "label_w_in": 2.0625, "label_h_in": 1.25,
    "margin_left_in": 0.125, "margin_top_in": 0.5,
    "col_pitch_in": 2.0625, "row_pitch_in": 1.25,
    "start_cell": 1
  }
}
```

---

## 9. Build order (milestones)

1. **Data core** — `tag_db_build.py` builds the `items`+`tokens` schema with the
   one-bucket resolver and conflict report. Verify resolution against known tokens.
2. **DMSi live price** — session manager + `ItemPriceAndAvailabilityList` (cust 1) with
   `ItemAuditResults` checking. Confirm against the sample tag ($36.99 / EA).
3. **Thermal renderer + RAW spool** — ZPL from the layout above; test-print to ZQ620;
   tune fonts on the 574x406 canvas.
4. **Mobile UI** — scan -> resolve -> live price -> print. The primary floor loop.
5. **Sheet renderer** — reportlab OR4P, calibration mode, partial-sheet; lock geometry.
6. **Desktop batch builder** — queue (paste + scan), preview, sheet print.
7. Polish: health check, recent prints, error states.

---

## 10. Open / calibration items
- Lock OR4P top-vs-bottom margin and yellow-end orientation with one calibration print.
- Confirm thermal RAW passthrough on the shared ZQ620 driver (ZDesigner/Generic).
- Fix the xref UPC export to emit **text** (kills the scientific-notation corruption).
- Decide a default barcode for a *brand-new* item printed thermally with nothing scanned
  (currently deferred; primary UPC is the natural choice if/when needed).

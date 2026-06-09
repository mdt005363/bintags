"""Flask backend: token resolution, live price, thermal + sheet printing.

Run:  python -m src.app      (serves web/ on config server.port)
"""
import os
import sqlite3

from flask import Flask, jsonify, request, send_from_directory, Response

from . import config
from .dmsi_session import DmsiSession
from .renderers import zpl as zpl_renderer
from .renderers import sheet_pdf
from . import print_broker

CFG = config.load()
DB = config.root_path(CFG["db"]["path"])
WEB = config.root_path("web")

app = Flask(__name__, static_folder=None)
_dmsi = DmsiSession(CFG)


def _db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def _resolve_token(token):
    con = _db()
    try:
        row = con.execute(
            "SELECT t.token, t.item_code, t.source, i.* FROM tokens t "
            "LEFT JOIN items i ON i.item_code = t.item_code WHERE t.token = ?",
            (token,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def _live(record):
    """Attach live price; fall back to cached price on DMSi error."""
    try:
        p = _dmsi.price_and_availability(record["item_code"], record.get("selling_uom") or "")
        record["price"] = p["price"] if p["price"] is not None else record.get("cached_price")
        record["on_hand"] = p["on_hand"]
        record["available"] = p["available"]
        record["audit"] = p["audit"]
        record["price_source"] = "live" if p["price"] is not None else "cached"
    except Exception as e:  # noqa: BLE001
        record["price"] = record.get("cached_price")
        record["price_source"] = "cached"
        record["price_error"] = str(e)
    return record


# ---- static ---------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(WEB, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(WEB, path)


# ---- api ------------------------------------------------------------------
@app.route("/api/resolve")
def api_resolve():
    token = (request.args.get("token") or "").strip()
    if not token:
        return jsonify({"ok": False, "error": "no token"}), 400
    rec = _resolve_token(token)
    if not rec:
        return jsonify({"ok": False, "found": False, "token": token})
    _live(rec)
    rec["scanned_token"] = token
    return jsonify({"ok": True, "found": True, "item": rec})


@app.route("/api/print/thermal", methods=["POST"])
def api_print_thermal():
    body = request.get_json(force=True)
    token = (body.get("token") or "").strip()
    copies = int(body.get("copies", 1))
    rec = _resolve_token(token)
    if not rec:
        return jsonify({"ok": False, "error": "token not found"}), 404
    _live(rec)
    z = zpl_renderer.render_thermal(rec, token, copies=copies)
    try:
        status = print_broker.send_zpl(z, CFG)
        return jsonify({"ok": True, "status": status, "price_source": rec.get("price_source")})
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(e), "zpl": z}), 500


@app.route("/api/batch/resolve", methods=["POST"])
def api_batch_resolve():
    body = request.get_json(force=True)
    tokens = body.get("tokens", [])
    out = []
    for tok in tokens:
        tok = str(tok).strip()
        if not tok:
            continue
        rec = _resolve_token(tok)
        if rec:
            _live(rec)
            rec["barcode_value"] = rec.get("primary_upc") or rec.get("item_code")
            out.append({"found": True, "token": tok, "item": rec})
        else:
            out.append({"found": False, "token": tok})
    return jsonify({"ok": True, "rows": out})


@app.route("/api/print/sheet", methods=["POST"])
def api_print_sheet():
    body = request.get_json(force=True)
    records = body.get("records", [])
    start_cell = int(body.get("start_cell", 1))
    pdf = sheet_pdf.render_sheet(records, CFG, start_cell=start_cell)
    if body.get("preview"):
        return Response(pdf, mimetype="application/pdf")
    status = print_broker.print_pdf(pdf, CFG)
    return jsonify({"ok": True, "status": status})


@app.route("/api/calibrate/sheet")
def api_calibrate():
    pdf = sheet_pdf.calibration_pdf(CFG)
    return Response(pdf, mimetype="application/pdf")


@app.route("/api/health")
def api_health():
    db_ok = os.path.exists(DB)
    try:
        con = _db()
        n = con.execute("SELECT count(*) FROM tokens").fetchone()[0]
        con.close()
    except Exception:  # noqa: BLE001
        n = None
    return jsonify({"db": db_ok, "tokens": n})


if __name__ == "__main__":
    s = CFG.get("server", {})
    app.run(host=s.get("host", "0.0.0.0"), port=s.get("port", 8080), debug=True)

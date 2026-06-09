"""Render bin tags onto a Centurion UN OR4P laser sheet (8.5x11, 4x8 = 32 labels).

Geometry comes from config["sheet"] (measured off the real sheet; fine-tune once with
the calibration grid). Barcode value = authoritative UPC (item-code fallback), since a
batch sheet has no scan. Code 128 symbology. Partial-sheet via start_cell.
"""
import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128


def _geom(cfg):
    s = cfg["sheet"]
    pw, ph = letter
    return {
        "pw": pw, "ph": ph,
        "cols": s["cols"], "rows": s["rows"],
        "lw": s["label_w_in"] * inch, "lh": s["label_h_in"] * inch,
        "ml": s["margin_left_in"] * inch, "mt": s["margin_top_in"] * inch,
        "cpx": s["col_pitch_in"] * inch, "cpy": s["row_pitch_in"] * inch,
        "per_page": s["cols"] * s["rows"],
    }


def _cell_origin(g, idx):
    """idx 0-based within a page -> (x_left, y_bottom) in reportlab coords."""
    col = idx % g["cols"]
    row = idx // g["cols"]
    x_left = g["ml"] + col * g["cpx"]
    y_top = g["mt"] + row * g["cpy"]
    y_bottom = g["ph"] - (y_top + g["lh"])
    return x_left, y_bottom


def _price(p):
    try:
        return f"${float(p):.2f}"
    except (TypeError, ValueError):
        return ""


def _draw_label(c, g, x, y, rec):
    w, h = g["lw"], g["lh"]
    pad = 4
    # description (top, small, up to 2 lines)
    desc = " ".join(v for v in [rec.get("description"), rec.get("extended_desc")] if v)
    c.setFont("Helvetica-Bold", 6)
    lines = simpleSplit(desc, "Helvetica-Bold", 6, w - 2 * pad)[:2]
    ty = y + h - pad - 6
    for ln in lines:
        c.drawString(x + pad, ty, ln)
        ty -= 7
    # price (prominent, right side mid)
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(x + w - pad, y + h * 0.42, _price(rec.get("price")))
    # uom (under price)
    c.setFont("Helvetica", 6)
    c.drawRightString(x + w - pad, y + h * 0.42 - 8, str(rec.get("uom") or ""))
    # item / part (left mid)
    c.setFont("Helvetica", 6)
    c.drawString(x + pad, y + h * 0.42, str(rec.get("part_number") or rec.get("item_code") or ""))
    c.drawString(x + pad, y + h * 0.42 - 8, str(rec.get("item_code") or ""))
    # barcode + human number (bottom, centered)
    token = str(rec.get("barcode_value") or rec.get("item_code") or "")
    if token:
        bc = code128.Code128(token, barHeight=20, barWidth=0.62, humanReadable=False)
        bx = x + (w - bc.width) / 2
        bc.drawOn(c, bx, y + pad + 6)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + w / 2, y + pad, token)


def render_sheet(records, cfg, start_cell=1):
    """records: list of dicts (description, extended_desc, part_number, item_code,
    price, uom, barcode_value). Returns PDF bytes."""
    g = _geom(cfg)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    slot = max(0, start_cell - 1)  # global 0-based slot across pages
    placed_on_page = False
    for rec in records:
        page_idx = slot % g["per_page"]
        if page_idx == 0 and placed_on_page:
            c.showPage()
        x, y = _cell_origin(g, page_idx)
        _draw_label(c, g, x, y, rec)
        placed_on_page = True
        slot += 1
    c.showPage()
    c.save()
    return buf.getvalue()


def calibration_pdf(cfg):
    """Cell outlines + crosshairs + numbers, to dial in margins/pitch and orientation."""
    g = _geom(cfg)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica", 7)
    for idx in range(g["per_page"]):
        x, y = _cell_origin(g, idx)
        c.rect(x, y, g["lw"], g["lh"])
        c.line(x, y + g["lh"] / 2, x + g["lw"], y + g["lh"] / 2)
        c.line(x + g["lw"] / 2, y, x + g["lw"] / 2, y + g["lh"])
        c.drawString(x + 3, y + g["lh"] - 9, f"cell {idx + 1}")
    c.drawString(g["ml"], g["ph"] - 14, "OR4P calibration — verify cell 1 aligns top-left; adjust config sheet.* if not")
    c.showPage()
    c.save()
    return buf.getvalue()

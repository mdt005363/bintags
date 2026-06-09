"""Render the bin tag as ZPL for the Zebra ZQ620 Plus (203 dpi, 574 x 406 dots).

The printer only burns dark; the yellow is pre-printed media. Barcode value is the
scanned token (round-trip). Code 128 symbology.
"""

PW = 574
LL = 406


def _z(s):
    """Escape ZPL control chars in field data."""
    if s is None:
        return ""
    return str(s).replace("^", " ").replace("~", " ").replace("\\", " ").strip()


def _price(p):
    try:
        return f"${float(p):.2f}"
    except (TypeError, ValueError):
        return ""


def render_thermal(record, token, copies=1):
    """record: dict with description, extended_desc, part_number, item_code, price, uom.
    token:   the value to encode in the barcode + print as the human-readable number.
    Returns a ZPL string ready to spool RAW.
    """
    desc = _z(" ".join(x for x in [record.get("description"), record.get("extended_desc")] if x))
    part = _z(record.get("part_number") or record.get("item_code"))
    item = _z(record.get("item_code"))
    price = _price(record.get("price"))
    uom = _z(record.get("uom"))
    tok = _z(token)

    z = []
    z.append("^XA")
    z.append(f"^PW{PW}")
    z.append(f"^LL{LL}")
    z.append("^CI28")
    z.append(f"^PQ{int(copies)}")
    # description — bold, wrap to 2 lines, clip overflow
    z.append(f"^FO20,14^A0N,40,40^FB{PW-40},2,0,L^FD{desc}^FS")
    # part # and item code (left)
    z.append(f"^FO20,206^A0N,30,30^FD{part}^FS")
    z.append(f"^FO20,248^A0N,30,30^FD{item}^FS")
    # price — large, right-justified
    z.append(f"^FO11,116^A0N,80,80^FB{PW-22},1,0,R^FD{price}^FS")
    # UOM — right, under price
    z.append(f"^FO11,256^A0N,34,34^FB{PW-22},1,0,R^FD{uom}^FS")
    # human-readable number — centered above barcode
    z.append(f"^FO0,300^A0N,26,26^FB{PW},1,0,C^FD{tok}^FS")
    # barcode — Code 128, in the white strip
    z.append("^BY2,2,76")
    z.append(f"^FO57,330^BCN,76,N,N,N^FD{tok}^FS")
    z.append("^XZ")
    return "\n".join(z)

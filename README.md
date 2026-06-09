# HIO Bin-Tag App

BarTender replacement for Home Improvement Outlet. Scan a number → resolve to the
item → fetch the **live** DMSi price → print a tag to the wearable Zebra ZQ620
(thermal) or a Centurion UN OR4P 32-up laser sheet. One responsive UI for phone
(floor) and desktop (batch). Read-only against DMSi (reprint-to-match; no write-back).

Full design + decisions are in **`CLAUDE.md`** — read that first. Endpoint payloads
are in `reference/DMSi_Agility_API_v619_reference.md`.

## Setup
```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy config.example.json config.json               # then edit config.json
```
Fill `config.json`: DMSi `base_url` + `password`, the thermal `printer_share`
(e.g. `\\HOST\ZQ620`) and/or `printer_ip`, and the laser printer.
**`config.json` is gitignored — never commit the password.**

## Build the lookup DB (do this first, milestone 1)
```bash
python -m src.dmsi_inventory_export   # pull items/prices/descriptions -> data/inventory_export.json
python -m src.tag_db_build            # build data/hio_items.db + token_conflicts_<date>.xlsx
```
`tag_db_build` runs with just `data/xref.xlsx` too (tokens resolve; descriptions/prices
stay blank until the export runs). The conflict report lists every token that violates
the one-bucket rule (one number → two items) for cleanup in DMSi.

## Run
```bash
python -m src.app          # http://<host>:8080
```
Phone: open the URL, scan/type, see live price, Print tag.
Desktop: Batch sheet tab → paste/scan a list → Resolve → Preview/Print.
Print the **Calibration sheet** once and confirm cell 1 lines up before a full run;
adjust `config.json` `sheet.*` if needed.

## Notes / known items
- The DMSi response field names in `dmsi_session.py` (`Price`, `OnHand`, …) are matched
  by a broad search; confirm against one live call and pin them down.
- Thermal printing uses RAW spool (pywin32) on Windows, with a raw TCP :9100 fallback.
- Fix the upstream xref export to emit the UPC column as **text** — scientific-notation
  values (`8.85911E+11`) are corrupted before this app sees them and can't be recovered.

## Layout
```
CLAUDE.md            full brief / spec
config.example.json  template (copy to config.json)
reference/           API ref, OR4P sheet PDF, thermal tag sample
data/                xref.xlsx (sample); exports + DB land here (gitignored)
src/                 tag_db_build, dmsi_session, dmsi_inventory_export,
                     print_broker, app, renderers/{zpl,sheet_pdf}
web/                 index.html, app.js, styles.css
```

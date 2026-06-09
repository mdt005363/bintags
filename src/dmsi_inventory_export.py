"""Pull the full item scope from DMSi via Inventory/ItemsInChunksList and write
inventory_export.json. Replaces the old bartender-era export.

Run:  python -m src.dmsi_inventory_export
"""
import json

from . import config
from .dmsi_session import DmsiSession, _find_first

CHUNK = 3000  # tune to System Config max chunk size


def run_export(cfg=None, out_path=None):
    cfg = cfg or config.load()
    out_path = out_path or config.root_path(cfg["files"]["inventory_json"])
    sess = DmsiSession(cfg)
    sess.login()

    items = []
    pointer = 0
    while True:
        payload = {
            "request": {
                "dsItemsInChunksListRequest": {
                    "dtItemsInChunksListRequest": [{
                        "SearchBy": "",
                        "SearchValue": "",
                        "ChunkStartPointer": pointer,
                        "IncludeNonStock": True,
                        "IncludeNonSaleable": True,
                        "IncludePriceData": True,
                        "IncludeQuantityData": True,
                        "RecordFetchLimit": CHUNK,
                    }]
                }
            }
        }
        data = sess.post("Inventory/ItemsInChunksList", payload)
        rows = _extract_rows(data)
        items.extend(rows)
        more = _find_first(data, ("MoreResultsAvailable",))
        nxt = _find_first(data, ("NextChunkStartPointer",))
        print(f"  fetched {len(rows)} (total {len(items)}), more={more}")
        if not more or not rows:
            break
        pointer = int(nxt) if nxt is not None else pointer + CHUNK

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f)
    print(f"Wrote {len(items)} items -> {out_path}")
    return items


def _extract_rows(data):
    """Find the dt* result array of item rows in the response."""
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.startswith("dt") and isinstance(v, list) and v and isinstance(v[0], dict):
                    yield from v
                else:
                    yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
    rows = list(walk(data))
    return rows


if __name__ == "__main__":
    run_export()

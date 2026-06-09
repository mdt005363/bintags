"""DMSi Agility public API session manager (read-only usage for this app).

Holds one persistent ContextId from Session/Login and reuses it across calls,
refreshing automatically if the session expires. All requests are POST with the
ContextId + Branch headers (except Login).

Payload convention: request -> ds<Name> -> dt<Name> -> [ {fields} ], casing-sensitive.
See reference/DMSi_Agility_API_v619_reference.md for the full endpoint set.
"""
import threading
import requests


class DmsiError(RuntimeError):
    pass


class DmsiSession:
    def __init__(self, cfg):
        d = cfg["dmsi"]
        self.base_url = d["base_url"].rstrip("/")
        self.branch = d["branch"]
        self.login_id = d["login_id"]
        self.password = d["password"]
        self.customer_id = d.get("customer_id", "1")
        self._ctx = None
        self._lock = threading.Lock()
        self._session = requests.Session()

    # ----- low level -------------------------------------------------------
    def _url(self, service_method):
        return f"{self.base_url}/{service_method}"

    def login(self):
        with self._lock:
            r = self._session.post(
                self._url("Session/Login"),
                json={"request": {"LoginID": self.login_id, "Password": self.password}},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            ctx = _find_first(data, ("SessionContextId", "ContextId"))
            if not ctx:
                raise DmsiError(f"Login returned no ContextId: {data}")
            self._ctx = ctx
            return ctx

    def post(self, service_method, payload, _retry=True):
        if not self._ctx:
            self.login()
        headers = {
            "ContextId": self._ctx,
            "Branch": self.branch,
            "Content-Type": "application/json",
        }
        r = self._session.post(self._url(service_method), json=payload, headers=headers, timeout=60)
        if r.status_code in (401, 403) and _retry:
            self.login()
            return self.post(service_method, payload, _retry=False)
        r.raise_for_status()
        return r.json()

    # ----- app-specific calls ---------------------------------------------
    def price_and_availability(self, item_code, uom="", qty=1):
        """Live cash-sale price + availability for one item (customer 1).

        Returns dict: {price, uom, on_hand, available, audit, raw}.
        ALWAYS surface `audit` to the user — a mispriced tag must never print silently.
        """
        payload = {
            "request": {
                "dsItemPriceAndAvailRequest": {
                    "dtPriceAndAvailRequest": [{
                        "CustomerID": self.customer_id,
                        "ShiptoSequence": 1,
                        "SaleType": "",
                        "DateToCalculatePriceFor": "",
                        "UseOrderRestrictions": True,
                    }],
                    "dtItemToProcessRequest": [{
                        "ItemCode": item_code,
                        "PartNumber": "",
                        "OrderQuantity": qty,
                        "UOM": uom,
                    }],
                }
            }
        }
        data = self.post("Inventory/ItemPriceAndAvailabilityList", payload)
        price = _find_first(data, ("Price", "ExtendedPrice", "NetPrice", "UnitPrice"))
        onhand = _find_first(data, ("OnHand", "QuantityOnHand"))
        avail = _find_first(data, ("Available", "QuantityAvailable"))
        audit = _collect_audit(data)
        return {
            "item_code": item_code,
            "price": _to_float(price),
            "uom": uom,
            "on_hand": _to_float(onhand),
            "available": _to_float(avail),
            "audit": audit,
            "raw": data,
        }

    def prices_for_batch(self, items):
        """items: list of (item_code, uom). One call returns the set."""
        payload = {
            "request": {
                "dsItemPriceAndAvailRequest": {
                    "dtPriceAndAvailRequest": [{
                        "CustomerID": self.customer_id,
                        "ShiptoSequence": 1,
                        "SaleType": "",
                        "DateToCalculatePriceFor": "",
                        "UseOrderRestrictions": True,
                    }],
                    "dtItemToProcessRequest": [
                        {"ItemCode": ic, "PartNumber": "", "OrderQuantity": 1, "UOM": uom}
                        for ic, uom in items
                    ],
                }
            }
        }
        return self.post("Inventory/ItemPriceAndAvailabilityList", payload)


# --------------------------------------------------------------------------
def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _find_first(obj, keys):
    """Depth-first search for the first of `keys` anywhere in nested dict/list."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] not in (None, ""):
                return obj[k]
        for v in obj.values():
            found = _find_first(v, keys)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_first(v, keys)
            if found is not None:
                return found
    return None


def _collect_audit(obj, out=None):
    """Pull any ItemAuditResults / audit messages so callers can check them."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "Audit" in k and isinstance(v, (list, dict)):
                out.append({k: v})
            else:
                _collect_audit(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_audit(v, out)
    return out

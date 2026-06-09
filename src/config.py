"""Load config.json (falls back to config.example.json for shape)."""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def root_path(*parts):
    return os.path.join(_ROOT, *parts)


def load(path=None):
    path = path or root_path("config.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Copy config.example.json to config.json and fill in "
            "the DMSi password and printer details."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

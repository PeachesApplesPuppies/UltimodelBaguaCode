"""Offline CIAAW reference values. Text precision is retained in the dataset."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "elements.json"
CATALOG = json.loads(DATA_PATH.read_text(encoding="utf-8"))
BY_SYMBOL = {row["symbol"]: row for row in CATALOG["elements"]}


def element_value(symbol, field):
    if symbol not in BY_SYMBOL or field not in {"Z", "Ar", "uncertainty"}:
        raise ValueError("Use element(symbol, Z), element(symbol, Ar), or element(symbol, uncertainty).")
    value = BY_SYMBOL[symbol][field]
    if value is None:
        raise ValueError(f"No abridged standard atomic weight is listed for {symbol}.")
    return float(value)

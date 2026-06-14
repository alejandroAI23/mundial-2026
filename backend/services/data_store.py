from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_JSON = DATA_DIR / "worldcup_data.json"
CLASSIFICATION_CSV = DATA_DIR / "worldcup_classification.csv"
TOP_SCORERS_CSV = DATA_DIR / "worldcup_top_scorers.csv"

EMPTY_DATA: dict[str, Any] = {
    "classification": [],
    "top_scorers": [],
    "matches": [],
    "teams": [],
    "stadiums": [],
    "metadata": {},
}


def load_data() -> dict[str, Any]:
    if not DATA_JSON.exists():
        return EMPTY_DATA.copy()
    try:
        with DATA_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in EMPTY_DATA.items():
            data.setdefault(key, value)
        return data
    except Exception:
        return EMPTY_DATA.copy()


def save_data(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    pd.DataFrame(data.get("classification", [])).to_csv(CLASSIFICATION_CSV, index=False)
    pd.DataFrame(data.get("top_scorers", [])).to_csv(TOP_SCORERS_CSV, index=False)


def csv_paths() -> dict[str, str]:
    return {
        "worldcup_data_json": str(DATA_JSON),
        "classification_csv": str(CLASSIFICATION_CSV),
        "top_scorers_csv": str(TOP_SCORERS_CSV),
    }

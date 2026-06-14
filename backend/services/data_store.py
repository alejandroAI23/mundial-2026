from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_JSON = DATA_DIR / "worldcup_data.json"
ADVANCED_PLAYER_STATS_JSON = DATA_DIR / "advanced_player_stats.json"
CLASSIFICATION_CSV = DATA_DIR / "worldcup_classification.csv"
TOP_SCORERS_CSV = DATA_DIR / "worldcup_top_scorers.csv"

EMPTY_DATA: dict[str, Any] = {
    "classification": [],
    "top_scorers": [],
    "matches": [],
    "teams": [],
    "stadiums": [],
    "advanced_player_stats": {},
    "metadata": {},
}


def _load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback


def load_data() -> dict[str, Any]:
    data = _load_json(DATA_JSON, EMPTY_DATA.copy())
    if not isinstance(data, dict):
        data = EMPTY_DATA.copy()
    for key, value in EMPTY_DATA.items():
        data.setdefault(key, value)
    if not data.get("advanced_player_stats"):
        data["advanced_player_stats"] = _load_json(ADVANCED_PLAYER_STATS_JSON, {})
    return data


def save_data(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with ADVANCED_PLAYER_STATS_JSON.open("w", encoding="utf-8") as f:
        json.dump(data.get("advanced_player_stats") or {}, f, ensure_ascii=False, indent=2)

    pd.DataFrame(data.get("classification", [])).to_csv(CLASSIFICATION_CSV, index=False)
    pd.DataFrame(data.get("top_scorers", [])).to_csv(TOP_SCORERS_CSV, index=False)


def csv_paths() -> dict[str, str]:
    return {
        "worldcup_data_json": str(DATA_JSON),
        "advanced_player_stats_json": str(ADVANCED_PLAYER_STATS_JSON),
        "classification_csv": str(CLASSIFICATION_CSV),
        "top_scorers_csv": str(TOP_SCORERS_CSV),
    }

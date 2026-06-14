from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_CACHE_JSON = DATA_DIR / "apifootball_raw_cache.json"


def empty_cache() -> dict[str, Any]:
    return {
        "fixtures": [],
        "players": [],
        "fixture_events": {},
        "fixture_players": {},
        "metadata": {},
    }


def load_raw_cache() -> dict[str, Any]:
    if not RAW_CACHE_JSON.exists():
        return empty_cache()
    try:
        with RAW_CACHE_JSON.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return empty_cache()
        base = empty_cache()
        base.update(data)
        return base
    except Exception:
        return empty_cache()


def save_raw_cache(cache: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with RAW_CACHE_JSON.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def set_cache_timestamp(cache: dict[str, Any], key: str) -> None:
    cache.setdefault("metadata", {})[key] = datetime.now(timezone.utc).isoformat()


def cache_age_hours(cache: dict[str, Any], key: str) -> float | None:
    raw = ((cache.get("metadata") or {}).get(key))
    if not raw:
        return None
    try:
        updated = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - updated).total_seconds() / 3600
    except Exception:
        return None

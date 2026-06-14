from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import requests

from .advanced_player_stats_service import (
    build_advanced_player_stats as _build_advanced_player_stats_from_api,
    get_player_ranking,
    normalize_metric,
)
from .balldontlie_client import (
    BalldontlieAPIError,
    BalldontlieConfigError,
    fetch_paginated,
    is_balldontlie_configured,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ADVANCED_STATS_FILE = DATA_DIR / "advanced_player_stats.json"

DEFAULT_BASE_URL = "https://api.balldontlie.io/v1"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", "null"):
            return default
        return int(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    return "" if value is None else str(value)


def _parse_birth_year(value: Any) -> int | None:
    try:
        if isinstance(value, (int, float)):
            return int(value)
        if not value:
            return None
        text = str(value)
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4])
        return date.fromisoformat(text).year
    except Exception:
        return None


def fetch_balldontlie(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    api_key = os.getenv("BALLDONTLIE_API_KEY", "").strip()
    base_url = os.getenv("BALLDONTLIE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if not api_key:
        return {"data": [], "meta": {"next_cursor": None}, "source": "missing_api_key"}

    url = f"{base_url}/{endpoint.lstrip('/')}"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {"data": []}
    except Exception as exc:
        return {"data": [], "meta": {"next_cursor": None}, "error": str(exc), "source": "request_error"}


def fetch_paginated_balldontlie(endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    cursor = None
    page_params = dict(params or {})

    while True:
        if cursor is not None:
            page_params["cursor"] = cursor
        payload = fetch_balldontlie(endpoint, page_params)
        data = payload.get("data") or []
        items.extend([item for item in data if isinstance(item, dict)])
        meta = payload.get("meta") or {}
        next_cursor = meta.get("next_cursor") or meta.get("nextPage")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor

    return items


def build_advanced_player_stats(
    players: list[dict[str, Any]] | None = None,
    rosters: list[dict[str, Any]] | None = None,
    match_events: list[dict[str, Any]] | None = None,
    player_stats: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if players is None and rosters is None and match_events is None and player_stats is None:
        return _build_advanced_player_stats_from_api()

    players = players or []
    rosters = rosters or []
    match_events = match_events or []
    player_stats = player_stats or []
    player_map = {
        str(item.get("id") or item.get("player_id") or ""): item
        for item in players
        if item.get("id") is not None or item.get("player_id") is not None
    }
    roster_map = {}
    for item in rosters:
        player_id = item.get("player_id") or item.get("player", {}).get("id")
        if player_id is not None:
            roster_map[str(player_id)] = item

    event_counts: dict[str, dict[str, Any]] = {}
    for event in match_events:
        player = event.get("player") or {}
        player_id = player.get("id") or event.get("player_id")
        if player_id is None:
            continue
        key = str(player_id)
        bucket = event_counts.setdefault(key, {
            "yellow_cards": 0,
            "red_cards": 0,
            "fouls_committed": 0,
            "goalkeeper_saves": 0,
            "substituted_out": 0,
        })
        event_type = str(event.get("type") or "").lower()
        if event_type in {"yellow_card", "yellow-card", "yellow"}:
            bucket["yellow_cards"] += 1
        elif event_type in {"red_card", "red-card", "red"}:
            bucket["red_cards"] += 1
        elif event_type in {"foul", "fouls", "foul_committed"}:
            bucket["fouls_committed"] += 1
        elif event_type in {"goalkeeper_save", "save", "saves"}:
            bucket["goalkeeper_saves"] += 1
        elif event_type in {"substitution", "substituted_out"}:
            bucket["substituted_out"] += 1

    stat_map = {}
    for stat in player_stats:
        player = stat.get("player") or {}
        player_id = player.get("id") or stat.get("player_id")
        if player_id is None:
            continue
        key = str(player_id)
        stat_map[key] = {
            "minutes_played": _safe_int(stat.get("minutes_played") or stat.get("minutes")),
            "fouls_committed": _safe_int(stat.get("fouls_committed") or stat.get("fouls")),
            "was_fouled": _safe_int(stat.get("was_fouled") or stat.get("fouled")),
            "goalkeeper_saves": _safe_int(stat.get("saves") or stat.get("goalkeeper_saves")),
        }

    rows = []
    for player_id, item in player_map.items():
        roster = roster_map.get(player_id, {})
        team = (roster.get("team") or {}).get("name") or roster.get("team_name") or roster.get("team") or "Sin equipo"
        birth_year = _parse_birth_year(item.get("date_of_birth") or item.get("birth_date"))
        current_year = date.today().year
        age_years = (current_year - birth_year) if birth_year else None

        event_bucket = event_counts.get(player_id, {
            "yellow_cards": 0,
            "red_cards": 0,
            "fouls_committed": 0,
            "goalkeeper_saves": 0,
            "substituted_out": 0,
        })
        stat_bucket = stat_map.get(player_id, {
            "minutes_played": 0,
            "fouls_committed": 0,
            "was_fouled": 0,
            "goalkeeper_saves": 0,
        })

        row = {
            "player_id": player_id,
            "player_name": f"{_safe_str(item.get('first_name'))} {_safe_str(item.get('last_name'))}".strip(),
            "team": team,
            "age_years": age_years,
            "minutes_played": stat_bucket["minutes_played"],
            "yellow_cards": event_bucket["yellow_cards"],
            "red_cards": event_bucket["red_cards"],
            "fouls_committed": stat_bucket["fouls_committed"],
            "was_fouled": stat_bucket["was_fouled"],
            "goalkeeper_saves": stat_bucket["goalkeeper_saves"],
            "substituted_out": event_bucket["substituted_out"],
            "youngest_rank": 0,
            "source": "balldontlie",
        }
        rows.append(row)

    rows.sort(key=lambda r: (-r["fouls_committed"], -r["minutes_played"], r["player_name"]))
    youngest_sorted = sorted(rows, key=lambda r: (r["age_years"] is None, r["age_years"] if r["age_years"] is not None else 999, r["player_name"]))
    for index, row in enumerate(youngest_sorted, start=1):
        for candidate in rows:
            if candidate["player_id"] == row["player_id"]:
                candidate["youngest_rank"] = index
                break

    return rows


def rank_advanced_player_stats(rows: list[dict[str, Any]], metric: str = "fouls_committed") -> list[dict[str, Any]]:
    allowed = {
        "minutes_played": "minutes_played",
        "yellow_cards": "yellow_cards",
        "red_cards": "red_cards",
        "fouls_committed": "fouls_committed",
        "goalkeeper_saves": "goalkeeper_saves",
        "substituted_out": "substituted_out",
        "was_fouled": "was_fouled",
        "youngest": "age_years",
    }
    field = allowed.get(metric.lower(), "fouls_committed")

    if field == "age_years":
        ordered = sorted(rows, key=lambda r: (r.get("age_years") is None, r.get("age_years") if r.get("age_years") is not None else 999, r.get("player_name", "")))
    else:
        ordered = sorted(rows, key=lambda r: (-_safe_int(r.get(field)), r.get("player_name", "")))

    return ordered


def load_advanced_player_stats() -> list[dict[str, Any]]:
    if not ADVANCED_STATS_FILE.exists():
        return []
    try:
        return json.loads(ADVANCED_STATS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_advanced_player_stats(rows: list[dict[str, Any]]) -> None:
    ADVANCED_STATS_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def refresh_advanced_player_stats() -> list[dict[str, Any]]:
    players = fetch_paginated_balldontlie("players", {"per_page": 100})
    rosters = fetch_paginated_balldontlie("games", {"per_page": 100})
    events = fetch_paginated_balldontlie("games", {"per_page": 100})
    stats = fetch_paginated_balldontlie("stats", {"per_page": 100})
    rows = build_advanced_player_stats(players, rosters, events, stats)
    save_advanced_player_stats(rows)
    return rows

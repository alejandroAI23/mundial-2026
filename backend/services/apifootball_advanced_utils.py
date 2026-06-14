from __future__ import annotations

import os
from typing import Any

SEASON = int(os.getenv("API_FOOTBALL_SEASON", "2026"))
WORLD_CUP_LEAGUE_ID = int(os.getenv("API_FOOTBALL_WORLD_CUP_LEAGUE_ID", "1"))
MAX_NEW_FIXTURES_PER_SYNC = int(os.getenv("API_FOOTBALL_MAX_NEW_FIXTURES_PER_SYNC", "12"))
PLAYERS_TTL_HOURS = int(os.getenv("API_FOOTBALL_PLAYERS_TTL_HOURS", "24"))
PLAYERS_MAX_PAGES = int(os.getenv("API_FOOTBALL_PLAYERS_MAX_PAGES", "80"))
FETCH_SEASON_PLAYERS = os.getenv("API_FOOTBALL_FETCH_SEASON_PLAYERS", "true").lower() == "true"

RANKING_METRICS = {
    "yellow_cards",
    "red_cards",
    "minutes_played",
    "fouls_committed",
    "was_fouled",
    "saves",
    "offsides",
    "substituted_out",
    "penalties_saved",
    "best_rating",
}

UNSUPPORTED_METRICS = {
    "penalty_committed": "API-FOOTBALL Free no garantiza penaltis cometidos por jugador de forma agregada. Se podría inferir desde eventos si el dato viene informado en cada partido.",
    "goals_conceded_goalkeeper": "API-FOOTBALL Free no garantiza goles encajados por portero de forma fiable sin procesar alineaciones y minutos de cada partido.",
}

METRIC_ALIASES = {
    "young": "youngest",
    "youngest_players": "youngest",
    "yellow": "yellow_cards",
    "yellows": "yellow_cards",
    "red": "red_cards",
    "reds": "red_cards",
    "expulsions": "red_cards",
    "minutes": "minutes_played",
    "fouls": "fouls_committed",
    "fouls_drawn": "was_fouled",
    "fouls_received": "was_fouled",
    "saves_goalkeeper": "saves",
    "goalkeeper_saves": "saves",
    "offside": "offsides",
    "offsides_player": "offsides",
    "substitutions_out": "substituted_out",
    "substituted": "substituted_out",
    "rating": "best_rating",
    "best_player": "best_rating",
    "man_of_the_match": "best_rating",
}


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", "null"):
            return default
        return int(float(value))
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, "", "null"):
            return default
        return float(value)
    except Exception:
        return default


def normalize_metric(metric: str) -> str:
    metric = (metric or "").strip().lower()
    return METRIC_ALIASES.get(metric, metric)


def fixture_id(fixture: dict[str, Any]) -> str:
    return str(((fixture.get("fixture") or {}).get("id")) or "")


def is_finished_fixture(fixture: dict[str, Any]) -> bool:
    status = ((fixture.get("fixture") or {}).get("status") or {})
    short = str(status.get("short") or "").upper()
    return short in {"FT", "AET", "PEN"}


def fixture_label(fixture: dict[str, Any]) -> str:
    teams = fixture.get("teams") or {}
    home = (teams.get("home") or {}).get("name") or "Local"
    away = (teams.get("away") or {}).get("name") or "Visitante"
    return f"{home} vs {away}"

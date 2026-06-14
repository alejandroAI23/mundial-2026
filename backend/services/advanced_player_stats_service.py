from __future__ import annotations

from typing import Any

from .balldontlie_client import fetch_paginated, is_balldontlie_configured, BalldontlieAPIError, BalldontlieConfigError

UNSUPPORTED_METRICS = {
    "offsides": "La fuente actual solo expone fueras de juego a nivel de equipo, no por jugador.",
}


def normalize_metric(metric: str) -> str:
    return metric.strip().lower().replace(" ", "_")


def build_advanced_player_stats(season: int = 2026) -> dict[str, Any]:
    players = fetch_paginated("players", {"seasons[]": [season]})
    return {"players": players, "rankings": {}, "metadata": {"source": "balldontlie", "players_count": len(players)}}


def get_player_ranking(data: dict[str, Any], metric: str, limit: int = 10) -> dict[str, Any]:
    return {"metric": normalize_metric(metric), "supported": True, "ranking": [], "source": "balldontlie"}

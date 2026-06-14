from __future__ import annotations

from typing import Any

from .apifootball_client import APIFootballAPIError, APIFootballConfigError, is_api_football_configured
from .apifootball_advanced_utils import normalize_metric, UNSUPPORTED_METRICS


def build_advanced_player_stats() -> dict[str, Any]:
    return {"players": [], "rankings": {}, "match_best_players": [], "unsupported_metrics": UNSUPPORTED_METRICS, "metadata": {"source": "api-football", "status": "pending"}}


def get_player_ranking(data: dict[str, Any], metric: str, limit: int = 10) -> dict[str, Any]:
    metric = normalize_metric(metric)
    if metric in UNSUPPORTED_METRICS:
        return {"metric": metric, "supported": False, "answer": UNSUPPORTED_METRICS[metric], "ranking": [], "source": "api-football"}
    advanced = data.get("advanced_player_stats") if isinstance(data, dict) and "advanced_player_stats" in data else data
    rows = ((advanced or {}).get("rankings", {}) if isinstance(advanced, dict) else {}).get(metric, [])
    return {"metric": metric, "supported": True, "ranking": rows[: max(1, min(limit, 100))], "source": "api-football", "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {}}


def get_match_best_players(data: dict[str, Any], limit: int = 20) -> dict[str, Any]:
    advanced = data.get("advanced_player_stats") if isinstance(data, dict) and "advanced_player_stats" in data else data
    rows = (advanced or {}).get("match_best_players", []) if isinstance(advanced, dict) else []
    return {"source": "api-football", "best_players": rows[: max(1, min(limit, 100))], "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {}}

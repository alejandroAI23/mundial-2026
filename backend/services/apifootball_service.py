from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .apifootball_advanced_utils import (
    MAX_NEW_FIXTURES_PER_SYNC,
    RANKING_METRICS,
    SEASON,
    UNSUPPORTED_METRICS,
    WORLD_CUP_LEAGUE_ID,
    normalize_metric,
    safe_float,
    safe_int,
)
from .apifootball_cache import load_raw_cache, save_raw_cache
from .apifootball_client import APIFootballAPIError, APIFootballConfigError, is_api_football_configured
from .apifootball_merger import finalize_rows, merge_events, merge_fixture_player_stats, merge_season_players
from .apifootball_sync import refresh_finished_fixture_details, refresh_fixtures, refresh_players_if_needed


def _build_rankings(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    rankings: dict[str, list[dict[str, Any]]] = {
        "youngest": sorted(
            [r for r in rows if r.get("date_of_birth")],
            key=lambda r: str(r.get("date_of_birth")),
            reverse=True,
        )[:50]
    }
    for metric in RANKING_METRICS:
        if metric == "best_rating":
            rankings[metric] = sorted([r for r in rows if safe_float(r.get(metric)) > 0], key=lambda r: (-safe_float(r.get(metric)), str(r.get("player") or "")))[:50]
        else:
            rankings[metric] = sorted([r for r in rows if safe_int(r.get(metric)) > 0], key=lambda r: (-safe_int(r.get(metric)), str(r.get("player") or "")))[:50]
    return rankings


def build_advanced_player_stats(season: int = SEASON, league_id: int = WORLD_CUP_LEAGUE_ID) -> dict[str, Any]:
    cache = load_raw_cache()
    refresh_fixtures(cache, league_id, season)
    refresh_players_if_needed(cache, league_id, season)
    refresh_finished_fixture_details(cache)
    save_raw_cache(cache)

    db: dict[str, dict[str, Any]] = {}
    merge_season_players(db, cache.get("players") or [])
    match_best_players = merge_fixture_player_stats(db, cache.get("fixture_players") or {}, cache.get("fixtures") or [])
    merge_events(db, cache.get("fixture_events") or {})
    rows = finalize_rows(db)

    return {
        "players": rows,
        "rankings": _build_rankings(rows),
        "match_best_players": match_best_players[:100],
        "unsupported_metrics": UNSUPPORTED_METRICS,
        "metadata": {
            "source": "api-football",
            "league_id": league_id,
            "season": season,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "players_count": len(rows),
            "fixtures_count": len(cache.get("fixtures") or []),
            "fixture_events_cached": len(cache.get("fixture_events") or {}),
            "fixture_players_cached": len(cache.get("fixture_players") or {}),
            "season_players_count": len(cache.get("players") or []),
            "max_new_fixtures_per_sync": MAX_NEW_FIXTURES_PER_SYNC,
        },
    }


def get_player_ranking(data: dict[str, Any], metric: str, limit: int = 10) -> dict[str, Any]:
    metric = normalize_metric(metric)
    limit = max(1, min(limit, 100))
    if metric in UNSUPPORTED_METRICS:
        return {"metric": metric, "supported": False, "answer": UNSUPPORTED_METRICS[metric], "ranking": [], "source": "api-football"}
    advanced = data.get("advanced_player_stats") if isinstance(data, dict) and "advanced_player_stats" in data else data
    rows = ((advanced or {}).get("rankings", {}) if isinstance(advanced, dict) else {}).get(metric, [])
    if not rows:
        return {"metric": metric, "supported": True, "answer": "Todavía no hay datos avanzados sincronizados para esa métrica. Configura API_FOOTBALL_KEY y ejecuta /api/sync.", "ranking": [], "source": "api-football", "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {}}
    return {"metric": metric, "supported": True, "ranking": rows[:limit], "source": "api-football", "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {}}


def get_match_best_players(data: dict[str, Any], limit: int = 20) -> dict[str, Any]:
    advanced = data.get("advanced_player_stats") if isinstance(data, dict) and "advanced_player_stats" in data else data
    rows = (advanced or {}).get("match_best_players", []) if isinstance(advanced, dict) else []
    return {"source": "api-football", "best_players": rows[: max(1, min(limit, 100))], "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {}}

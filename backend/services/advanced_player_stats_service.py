from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from .advanced_player_merge import merge_events, merge_match_stats, merge_players, merge_rosters
from .advanced_player_utils import METRICS, UNSUPPORTED_METRICS, normalize_metric, safe_int
from .balldontlie_client import (
    BalldontlieAPIError,
    BalldontlieConfigError,
    fetch_paginated,
    is_balldontlie_configured,
)

SEASON = int(os.getenv("BALLDONTLIE_SEASON", "2026"))


def build_advanced_player_stats(season: int = SEASON) -> dict[str, Any]:
    players = fetch_paginated("players", {"seasons[]": [season]})
    rosters = fetch_paginated("rosters", {"seasons[]": [season]})
    events = fetch_paginated("match_events")
    match_stats = fetch_paginated("player_match_stats")

    db: dict[str, dict[str, Any]] = {}
    merge_players(db, players)
    merge_rosters(db, rosters)
    merge_match_stats(db, match_stats)
    merge_events(db, events)

    rows = sorted(db.values(), key=lambda row: str(row.get("player") or ""))
    youngest = sorted(
        [row for row in rows if row.get("date_of_birth")],
        key=lambda row: str(row.get("date_of_birth")),
        reverse=True,
    )[:50]

    rankings = {"youngest": youngest}
    for metric in METRICS:
        rankings[metric] = sorted(
            [row for row in rows if safe_int(row.get(metric)) > 0],
            key=lambda row: (-safe_int(row.get(metric)), str(row.get("player") or "")),
        )[:50]

    return {
        "players": rows,
        "rankings": rankings,
        "unsupported_metrics": UNSUPPORTED_METRICS,
        "metadata": {
            "source": "balldontlie",
            "season": season,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "players_count": len(rows),
            "raw_players_count": len(players),
            "raw_rosters_count": len(rosters),
            "raw_events_count": len(events),
            "raw_player_match_stats_count": len(match_stats),
        },
    }


def get_player_ranking(data: dict[str, Any], metric: str, limit: int = 10) -> dict[str, Any]:
    metric = normalize_metric(metric)
    limit = max(1, min(limit, 100))
    if metric in UNSUPPORTED_METRICS:
        return {
            "metric": metric,
            "supported": False,
            "answer": UNSUPPORTED_METRICS[metric],
            "ranking": [],
            "source": "balldontlie",
        }

    advanced = data.get("advanced_player_stats") if "advanced_player_stats" in data else data
    rows = ((advanced or {}).get("rankings", {}) if isinstance(advanced, dict) else {}).get(metric, [])
    if not rows:
        return {
            "metric": metric,
            "supported": True,
            "answer": "Todavía no hay datos avanzados sincronizados para esa métrica. Configura BALLDONTLIE_API_KEY con acceso a endpoints avanzados y ejecuta /api/sync.",
            "ranking": [],
            "source": "balldontlie",
            "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {},
        }
    return {
        "metric": metric,
        "supported": True,
        "ranking": rows[:limit],
        "source": "balldontlie",
        "metadata": (advanced or {}).get("metadata", {}) if isinstance(advanced, dict) else {},
    }

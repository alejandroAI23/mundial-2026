from __future__ import annotations

from typing import Any

from .apifootball_advanced_utils import (
    MAX_NEW_FIXTURES_PER_SYNC,
    PLAYERS_MAX_PAGES,
    PLAYERS_TTL_HOURS,
    FETCH_SEASON_PLAYERS,
    fixture_id,
    is_finished_fixture,
)
from .apifootball_cache import cache_age_hours, set_cache_timestamp
from .apifootball_client import fetch_paginated, fetch_response


def refresh_fixtures(cache: dict[str, Any], league_id: int, season: int) -> None:
    cache["fixtures"] = fetch_response("fixtures", {"league": league_id, "season": season})
    set_cache_timestamp(cache, "fixtures_updated_at")


def refresh_players_if_needed(cache: dict[str, Any], league_id: int, season: int) -> None:
    if not FETCH_SEASON_PLAYERS:
        return
    age = cache_age_hours(cache, "players_updated_at")
    if cache.get("players") and age is not None and age < PLAYERS_TTL_HOURS:
        return
    cache["players"] = fetch_paginated(
        "players",
        {"league": league_id, "season": season},
        max_pages=PLAYERS_MAX_PAGES,
    )
    set_cache_timestamp(cache, "players_updated_at")


def refresh_finished_fixture_details(cache: dict[str, Any]) -> None:
    events_by_fixture = cache.setdefault("fixture_events", {})
    players_by_fixture = cache.setdefault("fixture_players", {})
    finished = [fixture for fixture in cache.get("fixtures", []) if is_finished_fixture(fixture)]
    pending = [
        fixture
        for fixture in finished
        if fixture_id(fixture) and (fixture_id(fixture) not in events_by_fixture or fixture_id(fixture) not in players_by_fixture)
    ]

    for fixture in pending[:MAX_NEW_FIXTURES_PER_SYNC]:
        fid = fixture_id(fixture)
        if fid not in events_by_fixture:
            events_by_fixture[fid] = fetch_response("fixtures/events", {"fixture": fid})
        if fid not in players_by_fixture:
            players_by_fixture[fid] = fetch_response("fixtures/players", {"fixture": fid})

    set_cache_timestamp(cache, "fixture_details_updated_at")

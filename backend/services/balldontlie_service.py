from __future__ import annotations

# Compatibilidad temporal: el código antiguo importaba balldontlie_service.
# Desde ahora la fuente avanzada principal es API-FOOTBALL.
from .apifootball_service import (
    APIFootballAPIError as BalldontlieAPIError,
    APIFootballConfigError as BalldontlieConfigError,
    build_advanced_player_stats,
    get_player_ranking,
    is_api_football_configured as is_balldontlie_configured,
)
from .apifootball_client import fetch_paginated
from .apifootball_advanced_utils import normalize_metric

__all__ = [
    "BalldontlieAPIError",
    "BalldontlieConfigError",
    "build_advanced_player_stats",
    "fetch_paginated",
    "get_player_ranking",
    "is_balldontlie_configured",
    "normalize_metric",
]

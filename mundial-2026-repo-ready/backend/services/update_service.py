"""Servicio de sincronización API -> JSON/CSV local."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from services.stats_service import (
    build_classification_from_games,
    build_classification_from_groups,
    build_top_scorers,
    save_outputs,
)
from services.worldcup_client import WorldCupClient


def refresh_worldcup_data() -> dict[str, Any]:
    client = WorldCupClient()
    raw = client.all_data()
    classification = build_classification_from_groups(raw.get("groups", []))
    if not classification:
        classification = build_classification_from_games(raw.get("games", []), raw.get("teams", []))
    top_scorers = build_top_scorers(raw.get("games", []))

    payload = {
        "metadata": {
            "source": "https://worldcup26.ir",
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "note": "Datos sincronizados desde API gratuita World Cup 2026 y normalizados a JSON/CSV.",
        },
        "classification": classification,
        "top_scorers": top_scorers,
        "games": raw.get("games", []),
        "teams": raw.get("teams", []),
        "groups": raw.get("groups", []),
        "stadiums": raw.get("stadiums", []),
    }
    files = save_outputs(payload)
    return {"status": "ok", "files": files, "metadata": payload["metadata"]}

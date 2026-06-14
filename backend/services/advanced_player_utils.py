from __future__ import annotations

from datetime import date, datetime
from typing import Any

TOURNAMENT_START = date(2026, 6, 11)

METRICS = [
    "yellow_cards",
    "red_cards",
    "minutes_played",
    "fouls_committed",
    "was_fouled",
    "saves",
    "saves_inside_box",
    "substituted_out",
]

UNSUPPORTED_METRICS = {
    "offsides": "La fuente actual solo expone fueras de juego a nivel de equipo, no por jugador.",
    "penalty_committed": "La fuente actual no expone penaltis cometidos por jugador de forma fiable.",
    "penalties_saved": "La fuente actual no consolida penaltis parados por portero como ranking directo.",
}

ALIASES = {
    "joven": "youngest",
    "mas_joven": "youngest",
    "edad": "youngest",
    "amarillas": "yellow_cards",
    "tarjetas_amarillas": "yellow_cards",
    "rojas": "red_cards",
    "expulsiones": "red_cards",
    "expulsados": "red_cards",
    "minutos": "minutes_played",
    "minutos_jugados": "minutes_played",
    "faltas_realizadas": "fouls_committed",
    "faltas_cometidas": "fouls_committed",
    "faltas_recibidas": "was_fouled",
    "paradas": "saves",
    "sustituido": "substituted_out",
    "sustituciones": "substituted_out",
    "fuera_de_juego": "offsides",
    "fueras_de_juego": "offsides",
    "penalti_cometido": "penalty_committed",
    "penaltis_parados": "penalties_saved",
}


def normalize_metric(metric: str) -> str:
    key = metric.strip().lower().replace(" ", "_").replace("-", "_")
    for old, new in {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}.items():
        key = key.replace(old, new)
    return ALIASES.get(key, key)


def safe_int(value: Any) -> int:
    try:
        return 0 if value in (None, "", "null") else int(float(value))
    except Exception:
        return 0


def age_from_birthdate(raw: Any) -> tuple[str | None, int | None]:
    if not raw:
        return None, None
    try:
        born = datetime.fromisoformat(str(raw).replace("Z", "+00:00")).date()
    except ValueError:
        try:
            born = datetime.strptime(str(raw)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None, None
    years = TOURNAMENT_START.year - born.year - ((TOURNAMENT_START.month, TOURNAMENT_START.day) < (born.month, born.day))
    return born.isoformat(), years


def player_id(player: dict[str, Any] | None, fallback: Any = None) -> str | None:
    if isinstance(player, dict) and player.get("id") is not None:
        return str(player["id"])
    return str(fallback) if fallback is not None else None

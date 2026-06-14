from __future__ import annotations

from typing import Any

from .apifootball_service import get_match_best_players, get_player_ranking
from .qa_service import answer_question as base_answer_question

LABELS = {
    "youngest": "más joven",
    "yellow_cards": "más tarjetas amarillas",
    "red_cards": "más tarjetas rojas/expulsiones",
    "minutes_played": "más minutos jugados",
    "fouls_committed": "más faltas cometidas",
    "was_fouled": "más faltas recibidas",
    "saves": "más paradas",
    "offsides": "más fueras de juego",
    "penalties_saved": "más penaltis parados",
    "substituted_out": "más veces sustituido",
    "best_rating": "mejor valoración individual",
}

VALUE_LABELS = {
    "yellow_cards": "amarillas",
    "red_cards": "rojas",
    "minutes_played": "minutos",
    "fouls_committed": "faltas cometidas",
    "was_fouled": "faltas recibidas",
    "saves": "paradas",
    "offsides": "fueras de juego",
    "penalties_saved": "penaltis parados",
    "substituted_out": "sustituciones saliendo",
    "best_rating": "de rating",
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    return text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")


def metric_from_question(question: str) -> str | None:
    q = normalize(question)
    if "mejor jugador" in q or "mvp" in q or "valoracion" in q:
        return "best_rating"
    if "fuera de juego" in q or "fueras de juego" in q or "offside" in q:
        return "offsides"
    if "penalti" in q and any(x in q for x in ["cometido", "provocado", "realizado"]):
        return "penalty_committed"
    if "penalti" in q and any(x in q for x in ["parado", "parados", "atajados", "salvados"]):
        return "penalties_saved"
    if "joven" in q or "edad" in q:
        return "youngest"
    if "amarilla" in q:
        return "yellow_cards"
    if "roja" in q or "expulsado" in q or "expulsiones" in q:
        return "red_cards"
    if "minuto" in q:
        return "minutes_played"
    if "falta" in q:
        return "was_fouled" if any(x in q for x in ["recib", "sufr", "le hacen"]) else "fouls_committed"
    if "portero" in q and any(x in q for x in ["menos goles", "goles encajados", "menos encajados"]):
        return "goals_conceded_goalkeeper"
    if "parada" in q or "portero" in q:
        return "saves"
    if "sustituido" in q or "sustituciones" in q or "cambiado" in q:
        return "substituted_out"
    return None


def format_player(row: dict[str, Any]) -> str:
    player = row.get("player") or "Jugador"
    team = row.get("team")
    return f"{player} ({team})" if team else str(player)


def format_value(row: dict[str, Any], metric: str) -> str:
    if metric == "youngest":
        if row.get("age") and row.get("date_of_birth"):
            return f"{row.get('age')} años, nacido el {row.get('date_of_birth')}"
        return f"nacido el {row.get('date_of_birth')}" if row.get("date_of_birth") else "edad no disponible"
    return f"{row.get(metric)} {VALUE_LABELS.get(metric, metric)}"


def answer_best_players_by_match(data: dict[str, Any]) -> dict[str, Any] | None:
    result = get_match_best_players(data.get("advanced_player_stats", {}), limit=5)
    rows = result.get("best_players", [])
    if not rows:
        return None
    lines = "; ".join(f"{r.get('match')}: {r.get('player')} ({r.get('team')}) con rating {r.get('rating')}" for r in rows[:3])
    return {"answer": f"Mejores jugadores por partido disponibles: {lines}.", "source": "api-football", "intent": "players", "data": rows, "metadata": result.get("metadata", {})}


def answer_advanced_question(question: str, data: dict[str, Any]) -> dict[str, Any] | None:
    q = normalize(question)
    if "por partido" in q and ("mejor jugador" in q or "mvp" in q):
        answer = answer_best_players_by_match(data)
        if answer:
            return answer

    metric = metric_from_question(question)
    if not metric:
        return None
    result = get_player_ranking(data.get("advanced_player_stats", {}), metric, limit=5)
    if not result.get("supported", True):
        return {"answer": result.get("answer"), "source": "api-football", "intent": "players", "metric": metric}
    ranking = result.get("ranking", [])
    if not ranking:
        return {"answer": result.get("answer", "Todavía no tengo datos avanzados sincronizados para esa pregunta."), "source": "api-football", "intent": "players", "metric": metric, "metadata": result.get("metadata", {})}

    metric = result.get("metric", metric)
    top = ranking[0]
    answer = f"El jugador con {LABELS.get(metric, metric)} es {format_player(top)} con {format_value(top, metric)}."
    if len(ranking) > 1:
        others = "; ".join(f"{idx}. {format_player(row)}: {format_value(row, metric)}" for idx, row in enumerate(ranking[1:4], start=2))
        answer += f" Top adicional: {others}."
    return {"answer": answer, "source": "api-football", "intent": "players", "metric": metric, "data": ranking, "metadata": result.get("metadata", {})}


def answer_question(question: str, data: dict[str, Any]) -> dict[str, Any]:
    advanced = answer_advanced_question(question, data)
    if advanced:
        return advanced
    return base_answer_question(question, data)

"""Motor QA híbrido para el Mundial 2026.

Primero intenta responder con reglas sobre JSON/CSV. Esto es más barato y fiable
para preguntas factuales: líder, clasificación, goleadores, próximos partidos.
Si no sabe responder, deja una respuesta clara y se puede conectar un modelo local.
"""

from __future__ import annotations

import re
from typing import Any


def normalize(text: str) -> str:
    text = text.lower().strip()
    replacements = str.maketrans("áéíóúüñ", "aeiouun")
    return text.translate(replacements)


def answer_question(question: str, data: dict[str, Any]) -> dict[str, Any]:
    q = normalize(question)
    classification = data.get("classification", []) or []
    top_scorers = data.get("top_scorers", []) or []
    games = data.get("games", []) or []

    if any(word in q for word in ["maximo goleador", "pichichi", "mas goles", "goleador"]):
        return answer_top_scorer(q, top_scorers)

    if any(word in q for word in ["clasificacion", "tabla", "grupo", "lider", "primero", "puntos"]):
        return answer_classification(q, classification)

    if any(word in q for word in ["partido", "juega", "proximo", "calendario", "hora"]):
        return answer_games(q, games)

    return {
        "answer": "Puedo responder sobre clasificación, puntos, máximos goleadores y próximos partidos. Prueba: '¿quién lidera el grupo A?' o '¿quién es el máximo goleador?'.",
        "source": "rules",
        "confidence": 0.35,
    }


def answer_top_scorer(q: str, top_scorers: list[dict[str, Any]]) -> dict[str, Any]:
    if not top_scorers:
        return {"answer": "Aún no tengo datos de goleadores en el JSON local.", "source": "rules", "confidence": 0.4}
    ordered = sorted(top_scorers, key=lambda r: int(r.get("goals") or 0), reverse=True)
    top = ordered[0]
    answer = f"El máximo goleador es {top.get('player')} ({top.get('team')}) con {top.get('goals')} goles."
    if "top" in q or "lista" in q or "ranking" in q:
        items = [f"{i+1}. {r.get('player')} ({r.get('team')}): {r.get('goals')} goles" for i, r in enumerate(ordered[:5])]
        answer = "Top goleadores:\n" + "\n".join(items)
    return {"answer": answer, "source": "top_scorers", "confidence": 0.9}


def answer_classification(q: str, classification: list[dict[str, Any]]) -> dict[str, Any]:
    if not classification:
        return {"answer": "Aún no tengo datos de clasificación en el JSON local.", "source": "rules", "confidence": 0.4}

    group_match = re.search(r"grupo\s+([a-l])", q)
    rows = classification
    if group_match:
        group = group_match.group(1).upper()
        rows = [r for r in rows if str(r.get("group", "")).upper() == group]
        if not rows:
            return {"answer": f"No tengo datos del Grupo {group} todavía.", "source": "classification", "confidence": 0.65}

    # Pregunta por equipo concreto
    for row in classification:
        team = normalize(str(row.get("team", "")))
        if team and team in q:
            return {
                "answer": f"{row.get('team')} tiene {row.get('points')} puntos en el Grupo {row.get('group')}. Lleva {row.get('played')} partidos, {row.get('wins')} victorias, {row.get('draws')} empates y {row.get('losses')} derrotas.",
                "source": "classification",
                "confidence": 0.88,
            }

    ordered = sorted(rows, key=lambda r: (int(r.get("points") or 0), int(r.get("goal_difference") or 0), int(r.get("goals_for") or 0)), reverse=True)
    leader = ordered[0]
    if group_match:
        return {"answer": f"El líder del Grupo {leader.get('group')} es {leader.get('team')} con {leader.get('points')} puntos.", "source": "classification", "confidence": 0.9}

    items = [f"{i+1}. {r.get('team')} ({r.get('group')}): {r.get('points')} pts" for i, r in enumerate(ordered[:5])]
    return {"answer": "Clasificación general por puntos:\n" + "\n".join(items), "source": "classification", "confidence": 0.82}


def answer_games(q: str, games: list[dict[str, Any]]) -> dict[str, Any]:
    if not games:
        return {"answer": "Aún no tengo partidos cargados en el JSON local.", "source": "rules", "confidence": 0.4}

    # Busca por equipo si aparece en la pregunta
    matched = []
    for g in games:
        home = str(g.get("home_team_name_en") or g.get("home_team") or "")
        away = str(g.get("away_team_name_en") or g.get("away_team") or "")
        if normalize(home) in q or normalize(away) in q:
            matched.append(g)
    if not matched:
        matched = games[:5]

    lines = []
    for g in matched[:5]:
        home = g.get("home_team_name_en") or g.get("home_team") or "Local"
        away = g.get("away_team_name_en") or g.get("away_team") or "Visitante"
        date = g.get("local_date") or g.get("date") or "fecha por confirmar"
        score = f"{g.get('home_score', '-')} - {g.get('away_score', '-')}"
        lines.append(f"{home} vs {away} · {date} · {score}")
    return {"answer": "Partidos encontrados:\n" + "\n".join(lines), "source": "games", "confidence": 0.75}

from __future__ import annotations

import re
from typing import Any


def normalize(text: str) -> str:
    return text.lower().strip()


def answer_question(question: str, data: dict[str, Any]) -> dict[str, Any]:
    q = normalize(question)
    classification = data.get("classification", []) or []
    scorers = data.get("top_scorers", []) or []

    if not question.strip():
        return {"answer": "Escribe una pregunta sobre clasificación, goleadores o partidos.", "source": "rules"}

    if any(x in q for x in ["maximo goleador", "máximo goleador", "goleador", "pichichi"]):
        if not scorers:
            return {"answer": "Todavía no tengo datos de goleadores actualizados.", "source": "rules"}
        top = sorted(scorers, key=lambda r: int(r.get("goals") or 0), reverse=True)[0]
        return {
            "answer": f"El máximo goleador es {top.get('player')} ({top.get('team')}) con {top.get('goals')} goles.",
            "source": "rules",
            "data": top,
        }

    group_match = re.search(r"grupo\s+([a-l])", q, re.IGNORECASE)
    if any(x in q for x in ["lider", "líder", "primero", "encabeza", "clasificacion", "clasificación"]):
        rows = classification
        if group_match:
            group = group_match.group(1).upper()
            rows = [r for r in rows if str(r.get("group", "")).upper() == group]
        if not rows:
            return {"answer": "No tengo clasificación disponible para esa consulta.", "source": "rules"}
        rows = sorted(rows, key=lambda r: (int(r.get("points") or 0), int(r.get("goal_difference") or 0), int(r.get("goals_for") or 0)), reverse=True)
        top = rows[0]
        suffix = f" del Grupo {top.get('group')}" if top.get("group") else ""
        return {
            "answer": f"El líder{suffix} es {top.get('team')} con {top.get('points')} puntos y diferencia de goles {top.get('goal_difference')}.",
            "source": "rules",
            "data": top,
        }

    # Points by team: matches common phrasing.
    if any(x in q for x in ["puntos", "cuantos puntos", "cuántos puntos"]):
        for row in classification:
            team = str(row.get("team", ""))
            if team and team.lower() in q:
                return {
                    "answer": f"{team} tiene {row.get('points')} puntos en el Grupo {row.get('group')}.",
                    "source": "rules",
                    "data": row,
                }

    if any(x in q for x in ["ayuda", "puedes", "preguntar", "opciones"]):
        return {
            "answer": "Puedes preguntarme: quién es el máximo goleador, quién lidera el grupo A, cuántos puntos tiene España, o pedirme la clasificación.",
            "source": "rules",
        }

    return {
        "answer": "No he entendido la pregunta. Prueba con: '¿Quién es el máximo goleador?', '¿Quién lidera el grupo A?' o '¿Cuántos puntos tiene España?'.",
        "source": "rules",
    }

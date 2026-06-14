from __future__ import annotations

import re
from typing import Any

from .stats_service import build_prediction


TEAM_ALIASES = {
    "españa": "Spain",
    "espana": "Spain",
    "méxico": "Mexico",
    "mexico": "Mexico",
    "estados unidos": "United States",
    "eeuu": "United States",
    "usa": "United States",
    "alemania": "Germany",
    "brasil": "Brazil",
    "argentina": "Argentina",
    "francia": "France",
    "inglaterra": "England",
    "portugal": "Portugal",
    "uruguay": "Uruguay",
    "australia": "Australia",
    "corea del sur": "South Korea",
    "corea": "South Korea",
    "japon": "Japan",
    "japón": "Japan",
    "belgica": "Belgium",
    "bélgica": "Belgium",
    "marruecos": "Morocco",
    "senegal": "Senegal",
    "italia": "Italy",
    "holanda": "Netherlands",
    "paises bajos": "Netherlands",
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    text = text.replace("ñ", "n")
    return text


def _team_from_query(q: str, classification: list[dict[str, Any]]) -> str | None:
    by_name = {normalize(str(r.get("team", ""))): str(r.get("team", "")) for r in classification}
    for alias, canonical in TEAM_ALIASES.items():
        if alias in q:
            return canonical
    for key in by_name:
        if key in q or q in key:
            return by_name[key]
    return None


TEAM_DISPLAY = {
    "Spain": "España",
    "Mexico": "México",
    "United States": "Estados Unidos",
    "Germany": "Alemania",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "France": "Francia",
    "England": "Inglaterra",
    "Portugal": "Portugal",
    "Uruguay": "Uruguay",
    "Australia": "Australia",
    "South Korea": "Corea del Sur",
    "Japan": "Japón",
    "Belgium": "Bélgica",
    "Morocco": "Marruecos",
    "Senegal": "Senegal",
    "Italy": "Italia",
    "Netherlands": "Países Bajos",
}


def _display_name(team: str) -> str:
    return TEAM_DISPLAY.get(team, team)


def _match_status(match: dict[str, Any]) -> str:
    finished = str(match.get("finished") or "").lower() in {"true", "1", "yes", "si"}
    elapsed = str(match.get("time_elapsed") or "").lower()
    if finished or elapsed in {"finished", "complete"}:
        return "finalizado"
    if elapsed and elapsed not in {"notstarted", "scheduled"}:
        return "en juego"
    return "programado"


def answer_question(question: str, data: dict[str, Any]) -> dict[str, Any]:
    q = normalize(question)
    classification = data.get("classification", []) or []
    scorers = data.get("top_scorers", []) or []
    matches = data.get("matches", []) or []

    if not question.strip():
        return {"answer": "Escribe una pregunta sobre clasificación, goleadores o partidos.", "source": "rules"}

    if any(x in q for x in ["maximo goleador", "maximo", "máximo goleador", "goleador", "pichichi"]):
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

    if any(x in q for x in ["puntos", "cuantos puntos", "cuántos puntos", "cuanto puntos", "cuánta"]):
        team = _team_from_query(q, classification)
        if team:
            matched = [row for row in classification if str(row.get("team", "")).lower() == team.lower()]
            if matched:
                row = matched[0]
                return {
                    "answer": f"{team} tiene {row.get('points')} puntos, {row.get('wins')} victorias y {row.get('goal_difference')} de diferencia de goles en el Grupo {row.get('group')}.",
                    "source": "rules",
                    "data": row,
                }
            return {"answer": f"No tengo datos de clasificación disponibles para {team} en este momento.", "source": "rules"}
        if classification:
            top = sorted(classification, key=lambda r: (int(r.get("points") or 0), int(r.get("goal_difference") or 0)), reverse=True)[:3]
            names = ", ".join(f"{r.get('team')} ({r.get('points')} pts)" for r in top)
            return {"answer": f"Clasificación destacada: {names}.", "source": "rules", "data": top}

    if any(x in q for x in ["cuando juega", "cuando juega", "siguiente partido", "proximo partido", "próximo partido", "calendario", "juega", "juega hoy"]):
        team = _team_from_query(q, classification)
        candidate = [m for m in matches if team and (normalize(str(m.get("home_team_name_en") or "")) == normalize(team) or normalize(str(m.get("away_team_name_en") or "")) == normalize(team))]
        if not candidate:
            candidate = [m for m in matches if str(m.get("finished") or "").lower() not in {"true", "1"}]
        if candidate:
            nxt = sorted(candidate, key=lambda m: str(m.get("local_date") or ""))[:1][0]
            home = str(nxt.get("home_team_name_en") or nxt.get("home_team") or "Local")
            away = str(nxt.get("away_team_name_en") or nxt.get("away_team") or "Visitante")
            return {
                "answer": f"El próximo partido de {team or 'la fase' } es {home} vs {away} · {nxt.get('local_date')} · {nxt.get('stadium') or 'Estadio pendiente'} · Estado: {_match_status(nxt)}.",
                "source": "rules",
                "data": nxt,
            }

    if any(x in q for x in ["resultado", "resultados", "ultimo resultado", "último resultado", "jugados", "finalizado"]):
        finished = [m for m in matches if str(m.get("finished") or "").lower() in {"true", "1", "yes", "si"}]
        if finished:
            last = sorted(finished, key=lambda m: str(m.get("local_date") or ""), reverse=True)[:3]
            lines = [f"{m.get('home_team_name_en')} {m.get('home_score', 0)} - {m.get('away_score', 0)} {m.get('away_team_name_en')}" for m in last]
            return {"answer": "Últimos resultados: " + " | ".join(lines) + ".", "source": "rules", "data": last}

    if any(x in q for x in ["estadio", "sede", "cancha", "stadium"]):
        team = _team_from_query(q, classification)
        candidate = [m for m in matches if team and (normalize(str(m.get("home_team_name_en") or "")) == normalize(team) or normalize(str(m.get("away_team_name_en") or "")) == normalize(team))]
        if candidate:
            nxt = sorted(candidate, key=lambda m: str(m.get("local_date") or ""))[:1][0]
            return {"answer": f"El próximo partido de {team} se juega en {nxt.get('stadium') or 'estadio pendiente'}.", "source": "rules", "data": nxt}

    if any(x in q for x in ["ganara", "ganará", "prediccion", "predicción", "quien gana", "quién gana"]):
        mentioned = []
        for alias, canonical in TEAM_ALIASES.items():
            if alias in q:
                mentioned.append(canonical)
        for key, value in {normalize(str(r.get("team", ""))): str(r.get("team", "")) for r in classification}.items():
            if key in q and value not in mentioned:
                mentioned.append(value)
        if len(set(mentioned)) >= 2:
            team_a, team_b = list(dict.fromkeys(mentioned))[:2]
        else:
            team_a = _team_from_query(q, classification)
            team_b = None
        if team_a and team_b:
            pred = build_prediction(classification, team_a, team_b)
            winner = pred.get("winner") or "Empate"
            winner_label = _display_name(winner) if winner in TEAM_DISPLAY else winner
            return {
                "answer": f"Predicción simple: {winner_label} tiene {int(pred.get('probability', 0) * 100)}% de probabilidad de ganar. {pred.get('explanation', '')}",
                "source": "rules",
                "data": pred,
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

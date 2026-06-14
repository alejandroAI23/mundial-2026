from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .apifootball_service import (
    APIFootballAPIError,
    APIFootballConfigError,
    build_advanced_player_stats,
    is_api_football_configured,
)
from .worldcup_client import get_games, get_groups, get_stadiums, get_teams


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", "null"):
            return default
        return int(value)
    except Exception:
        return default


def _status(game: dict[str, Any]) -> str:
    elapsed = str(game.get("time_elapsed") or game.get("elapsed") or "").lower()
    finished = str(game.get("finished") or "").upper() == "TRUE"
    if finished or elapsed == "finished":
        return "final"
    if elapsed and elapsed != "notstarted":
        return "live"
    return "scheduled"


def _team_name(team: dict[str, Any]) -> str:
    return team.get("name_en") or team.get("name") or team.get("team") or team.get("team_name") or "Equipo pendiente"


def _team_group(team: dict[str, Any]) -> str:
    return str(team.get("groups") or team.get("group") or team.get("group_name") or "").strip()


def _flag(team: dict[str, Any]) -> str:
    return str(team.get("flag") or team.get("flag_url") or "")


def build_classification_from_games(games: list[dict[str, Any]], teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table: dict[tuple[str, str], dict[str, Any]] = {}

    def ensure(team_name: str, group: str = "", flag: str = "") -> dict[str, Any]:
        key = (group or "Pendiente", team_name)
        if key not in table:
            table[key] = {"team": team_name, "group": group or "Pendiente", "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0, "points": 0, "flag": flag}
        elif flag and not table[key].get("flag"):
            table[key]["flag"] = flag
        return table[key]

    team_by_id = {str(t.get("id")): t for t in teams if t.get("id") is not None}
    for team in teams:
        ensure(_team_name(team), _team_group(team), _flag(team))

    for game in games:
        group = str(game.get("group") or game.get("group_name") or "").strip()
        if not group:
            continue
        home = game.get("home_team_name_en") or game.get("home_team") or game.get("home") or "Local pendiente"
        away = game.get("away_team_name_en") or game.get("away_team") or game.get("away") or "Visitante pendiente"
        home_row = ensure(home, group, _flag(team_by_id.get(str(game.get("home_team_id")), {})))
        away_row = ensure(away, group, _flag(team_by_id.get(str(game.get("away_team_id")), {})))
        if _status(game) != "final":
            continue
        hs, aw = _safe_int(game.get("home_score")), _safe_int(game.get("away_score"))
        home_row["played"] += 1; away_row["played"] += 1
        home_row["goals_for"] += hs; home_row["goals_against"] += aw
        away_row["goals_for"] += aw; away_row["goals_against"] += hs
        if hs > aw:
            home_row["wins"] += 1; home_row["points"] += 3; away_row["losses"] += 1
        elif aw > hs:
            away_row["wins"] += 1; away_row["points"] += 3; home_row["losses"] += 1
        else:
            home_row["draws"] += 1; away_row["draws"] += 1; home_row["points"] += 1; away_row["points"] += 1

    rows = []
    for row in table.values():
        row["goal_difference"] = row["goals_for"] - row["goals_against"]
        rows.append(row)
    rows.sort(key=lambda r: (r["group"], -r["points"], -r["goal_difference"], -r["goals_for"], r["team"]))
    return rows


def _parse_scorer_tokens(raw: Any) -> list[str]:
    if not raw or raw == "null":
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, dict):
        return [str(v).strip() for v in raw.values() if str(v).strip()]
    text = str(raw).replace("{", "").replace("}", "").replace('"', "").replace("'", "").replace("[", "").replace("]", "")
    out = []
    for part in re.split(r",|;|\n", text):
        part = part.strip()
        if not part or part.lower() == "null":
            continue
        part = re.sub(r"^\d+\s*[:\-]\s*", "", part)
        part = re.sub(r"\s*\(?\d{1,3}['’]?\)?\s*$", "", part).strip()
        if part:
            out.append(part)
    return out


def build_top_scorers(games: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scorers: dict[tuple[str, str], int] = {}
    def add(player: str, team: str) -> None:
        scorers[(player, team)] = scorers.get((player, team), 0) + 1
    for game in games:
        home_team = game.get("home_team_name_en") or "Equipo local"
        away_team = game.get("away_team_name_en") or "Equipo visitante"
        for player in _parse_scorer_tokens(game.get("home_scorers") or game.get("home_goals")):
            add(player, home_team)
        for player in _parse_scorer_tokens(game.get("away_scorers") or game.get("away_goals")):
            add(player, away_team)
        for goal in game.get("goals", []) if isinstance(game.get("goals"), list) else []:
            player = goal.get("scorer") or goal.get("player")
            team = goal.get("team") or goal.get("team_name") or goal.get("teamName")
            if player and team:
                add(str(player), str(team))
    rows = [{"player": player, "team": team, "goals": goals, "age": None, "position": None} for (player, team), goals in scorers.items()]
    rows.sort(key=lambda r: (-r["goals"], r["player"]))
    return rows


def build_prediction(classification: list[dict[str, Any]], team_a: str, team_b: str) -> dict[str, Any]:
    by_name = {str(r.get("team", "")).lower(): r for r in classification}
    a, b = by_name.get(team_a.lower()), by_name.get(team_b.lower())
    if not a or not b:
        return {"team_a": team_a, "team_b": team_b, "winner": None, "probability": 0.5, "explanation": "No hay datos suficientes de clasificación para calcular una predicción."}
    def score(row: dict[str, Any]) -> float:
        return float(row.get("points", 0)) * 3 + float(row.get("goal_difference", 0)) * 1.2 + float(row.get("goals_for", 0)) * 0.6 - float(row.get("goals_against", 0)) * 0.4
    probability = 1 / (1 + pow(2.71828, -(score(a) - score(b)) / 8))
    winner = team_a if probability >= 0.5 else team_b
    winner_probability = probability if probability >= 0.5 else 1 - probability
    return {"team_a": team_a, "team_b": team_b, "winner": winner, "probability": round(float(winner_probability), 3), "explanation": "Predicción heurística basada en puntos, diferencia de goles y goles a favor. No es una apuesta ni una garantía."}


def _try_build_advanced_player_stats() -> tuple[dict[str, Any], str]:
    if not is_api_football_configured():
        return {}, "skipped: API_FOOTBALL_KEY no configurada"
    try:
        return build_advanced_player_stats(), "ok"
    except (APIFootballAPIError, APIFootballConfigError) as exc:
        return {}, f"unavailable: {exc}"
    except Exception as exc:
        return {}, f"error: {exc}"


def update_all_data() -> dict[str, Any]:
    games, teams, stadiums = get_games(), get_teams(), get_stadiums()
    try:
        groups = get_groups()
    except Exception:
        groups = []
    advanced_player_stats, advanced_status = _try_build_advanced_player_stats()
    return {
        "classification": build_classification_from_games(games, teams),
        "top_scorers": build_top_scorers(games),
        "matches": games,
        "teams": teams,
        "stadiums": stadiums,
        "advanced_player_stats": advanced_player_stats,
        "metadata": {"source": "worldcup26.ir", "advanced_source": "api-football", "advanced_player_stats_status": advanced_status, "updated_at": datetime.now(timezone.utc).isoformat(), "groups_raw_count": len(groups) if isinstance(groups, list) else None, "matches_count": len(games), "teams_count": len(teams), "stadiums_count": len(stadiums)},
    }

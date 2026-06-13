"""Normalización de datos deportivos para el portal Mundial 2026."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_FILE = DATA_DIR / "worldcup_data.json"
CLASSIFICATION_CSV = DATA_DIR / "worldcup_classification.csv"
TOP_SCORERS_CSV = DATA_DIR / "worldcup_top_scorers.csv"

TEAM_NAME_KEYS = ("name", "name_en", "team", "team_name", "country")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def first_present(data: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return default


def team_name(team: dict[str, Any] | str | None) -> str:
    if isinstance(team, str):
        return team
    if not isinstance(team, dict):
        return "Equipo pendiente"
    return str(first_present(team, TEAM_NAME_KEYS, "Equipo pendiente"))


def is_finished(game: dict[str, Any]) -> bool:
    finished = str(game.get("finished", "")).upper() == "TRUE"
    elapsed = str(game.get("time_elapsed", game.get("status", ""))).lower()
    return finished or elapsed in {"finished", "fulltime", "ft", "final"}


def game_team(game: dict[str, Any], side: str) -> str:
    # side: home / away
    return str(
        game.get(f"{side}_team_name_en")
        or game.get(f"{side}_team_name")
        or game.get(f"{side}TeamName")
        or game.get(f"{side}_team")
        or game.get(f"{side}Team")
        or "Equipo pendiente"
    )


def game_score(game: dict[str, Any], side: str) -> int:
    return safe_int(
        game.get(f"{side}_score")
        or game.get(f"{side}Score")
        or game.get(f"score_{side}")
        or 0
    )


def build_classification_from_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in groups:
        group_name = str(group.get("group") or group.get("name") or group.get("group_name") or "")
        standings = group.get("teams") or group.get("standings") or group.get("table") or []
        if not isinstance(standings, list):
            continue
        for item in standings:
            if not isinstance(item, dict):
                continue
            name = team_name(item)
            played = safe_int(first_present(item, ("played", "playedGames", "pj", "matches_played")))
            wins = safe_int(first_present(item, ("wins", "won", "g", "victories")))
            draws = safe_int(first_present(item, ("draws", "draw", "e")))
            losses = safe_int(first_present(item, ("losses", "lost", "p", "defeats")))
            gf = safe_int(first_present(item, ("goalsFor", "goals_for", "gf", "goals_scored")))
            ga = safe_int(first_present(item, ("goalsAgainst", "goals_against", "gc", "goals_conceded")))
            gd = safe_int(first_present(item, ("goalDifference", "goal_difference", "gd", "dg")), gf - ga)
            points = safe_int(first_present(item, ("points", "pts")))
            rows.append({
                "team": name,
                "group": group_name,
                "played": played,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "goals_for": gf,
                "goals_against": ga,
                "goal_difference": gd,
                "points": points,
            })
    return sorted(rows, key=lambda r: (r["group"], -r["points"], -r["goal_difference"], -r["goals_for"], r["team"]))


def build_classification_from_games(games: list[dict[str, Any]], teams: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Recalcula clasificación desde partidos finalizados.

    También mete equipos sin partidos, si vienen en /teams.
    """
    table: dict[tuple[str, str], dict[str, Any]] = {}

    def ensure(group: str, name: str) -> dict[str, Any]:
        key = (group, name)
        if key not in table:
            table[key] = {
                "team": name,
                "group": group,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "points": 0,
            }
        return table[key]

    if teams:
        for team in teams:
            if not isinstance(team, dict):
                continue
            group = str(team.get("groups") or team.get("group") or team.get("group_name") or "Pendiente")
            ensure(group, team_name(team))

    for game in games:
        group = str(game.get("group") or game.get("group_name") or game.get("stage") or "Pendiente")
        home = game_team(game, "home")
        away = game_team(game, "away")
        h = ensure(group, home)
        a = ensure(group, away)
        if not is_finished(game):
            continue
        hs = game_score(game, "home")
        aw = game_score(game, "away")
        h["played"] += 1
        a["played"] += 1
        h["goals_for"] += hs
        h["goals_against"] += aw
        a["goals_for"] += aw
        a["goals_against"] += hs
        if hs > aw:
            h["wins"] += 1
            h["points"] += 3
            a["losses"] += 1
        elif hs < aw:
            a["wins"] += 1
            a["points"] += 3
            h["losses"] += 1
        else:
            h["draws"] += 1
            a["draws"] += 1
            h["points"] += 1
            a["points"] += 1

    for row in table.values():
        row["goal_difference"] = row["goals_for"] - row["goals_against"]

    return sorted(table.values(), key=lambda r: (r["group"], -r["points"], -r["goal_difference"], -r["goals_for"], r["team"]))


def parse_scorer_string(value: Any) -> list[str]:
    """Parsea campos tipo home_scorers/away_scorers de la API.

    La API ha usado formatos variados: null, "[]", "{Jugador 12, Jugador 45+2}".
    Esta función es tolerante y devuelve nombres limpios.
    """
    if value in (None, "", "null", [], {}):
        return []
    if isinstance(value, list):
        raw_items = value
    else:
        text = str(value)
        text = text.replace("{", "").replace("}", "").replace("[", "").replace("]", "")
        text = text.replace('"', "").replace("'", "")
        raw_items = [x.strip() for x in text.split(",") if x.strip()]
    names: list[str] = []
    for item in raw_items:
        if isinstance(item, dict):
            name = item.get("scorer") or item.get("player") or item.get("name")
            if name:
                names.append(str(name).strip())
            continue
        text = str(item).strip()
        # Quita minuto final: "Messi 23'", "Messi (pen.) 45+2"
        text = re.sub(r"\s+\d{1,3}(\+\d+)?'?\s*$", "", text).strip()
        text = re.sub(r"\s*\((pen\.?|og|p)\)\s*", " ", text, flags=re.IGNORECASE).strip()
        if text:
            names.append(text)
    return names


def build_top_scorers(games: list[dict[str, Any]]) -> list[dict[str, Any]]:
    goals: dict[tuple[str, str], int] = defaultdict(int)
    for game in games:
        home = game_team(game, "home")
        away = game_team(game, "away")
        # Formato estructurado, si existe
        structured = game.get("goals") or game.get("events") or []
        if isinstance(structured, list):
            for event in structured:
                if not isinstance(event, dict):
                    continue
                if str(event.get("type", "goal")).lower() not in {"goal", "gol"}:
                    continue
                player = event.get("scorer") or event.get("player") or event.get("name")
                team = event.get("team") or event.get("teamName") or event.get("team_name")
                if player and team:
                    goals[(str(player).strip(), str(team).strip())] += 1

        for player in parse_scorer_string(game.get("home_scorers")):
            goals[(player, home)] += 1
        for player in parse_scorer_string(game.get("away_scorers")):
            goals[(player, away)] += 1

    rows = [
        {"player": player, "team": team, "goals": count, "age": "", "position": ""}
        for (player, team), count in goals.items()
    ]
    return sorted(rows, key=lambda r: (-r["goals"], r["player"], r["team"]))


def save_outputs(payload: dict[str, Any], data_dir: Path = DATA_DIR) -> dict[str, str]:
    data_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / "worldcup_data.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    classification = payload.get("classification", [])
    top_scorers = payload.get("top_scorers", [])

    write_csv(data_dir / "worldcup_classification.csv", classification, [
        "team", "group", "played", "wins", "draws", "losses", "goals_for", "goals_against", "goal_difference", "points",
    ])
    write_csv(data_dir / "worldcup_top_scorers.csv", top_scorers, [
        "player", "team", "goals", "age", "position",
    ])
    return {
        "json": str(data_dir / "worldcup_data.json"),
        "classification_csv": str(data_dir / "worldcup_classification.csv"),
        "top_scorers_csv": str(data_dir / "worldcup_top_scorers.csv"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def load_local_data(data_file: Path = DATA_FILE) -> dict[str, Any]:
    if not data_file.exists():
        return {"classification": [], "top_scorers": [], "games": [], "teams": [], "groups": [], "stadiums": []}
    with data_file.open("r", encoding="utf-8") as f:
        return json.load(f)

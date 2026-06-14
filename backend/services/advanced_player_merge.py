from __future__ import annotations

from typing import Any

from .advanced_player_utils import METRICS, age_from_birthdate, player_id, safe_int


def ensure_player(db: dict[str, dict[str, Any]], pid: str, player: dict[str, Any] | None = None) -> dict[str, Any]:
    row = db.setdefault(
        pid,
        {
            "player_id": pid,
            "player": None,
            "short_name": None,
            "team": None,
            "team_id": None,
            "position": None,
            "date_of_birth": None,
            "age": None,
            "appearances": 0,
            "starts": 0,
            "goals": 0,
            "assists": 0,
            **{metric: 0 for metric in METRICS},
        },
    )
    if isinstance(player, dict):
        row["player"] = row["player"] or player.get("name")
        row["short_name"] = row["short_name"] or player.get("short_name")
        row["team"] = row["team"] or player.get("country_name") or player.get("country_code")
        row["position"] = row["position"] or player.get("position")
        born, years = age_from_birthdate(player.get("date_of_birth"))
        if born and not row["date_of_birth"]:
            row["date_of_birth"], row["age"] = born, years
    return row


def merge_players(db: dict[str, dict[str, Any]], players: list[dict[str, Any]]) -> None:
    for player in players:
        pid = player_id(player)
        if pid:
            ensure_player(db, pid, player)


def merge_rosters(db: dict[str, dict[str, Any]], rosters: list[dict[str, Any]]) -> None:
    for item in rosters:
        player = item.get("player") if isinstance(item.get("player"), dict) else None
        pid = player_id(player, item.get("player_id"))
        if not pid:
            continue
        row = ensure_player(db, pid, player)
        row["team_id"] = row["team_id"] or item.get("team_id")
        row["position"] = row["position"] or item.get("position")
        for field in ["appearances", "starts", "minutes_played", "goals", "assists", "yellow_cards", "red_cards"]:
            row[field] = max(safe_int(row.get(field)), safe_int(item.get(field)))


def merge_match_stats(db: dict[str, dict[str, Any]], stats: list[dict[str, Any]]) -> None:
    minutes: dict[str, int] = {}
    for item in stats:
        pid = player_id(None, item.get("player_id"))
        if not pid:
            continue
        row = ensure_player(db, pid)
        row["team_id"] = row["team_id"] or item.get("team_id")
        minutes[pid] = minutes.get(pid, 0) + safe_int(item.get("minutes_played"))
        for field in ["fouls_committed", "was_fouled", "saves", "saves_inside_box"]:
            row[field] += safe_int(item.get(field))
    for pid, value in minutes.items():
        if not safe_int(db[pid].get("minutes_played")):
            db[pid]["minutes_played"] = value


def merge_events(db: dict[str, dict[str, Any]], events: list[dict[str, Any]]) -> None:
    for item in events:
        incident_type = str(item.get("incident_type") or "").lower()
        incident_class = str(item.get("incident_class") or "").lower()
        if incident_type == "substitution":
            player = item.get("player_out") if isinstance(item.get("player_out"), dict) else None
            pid = player_id(player)
            if pid:
                ensure_player(db, pid, player)["substituted_out"] += 1
        if incident_type == "card":
            player = item.get("player") if isinstance(item.get("player"), dict) else None
            pid = player_id(player)
            if not pid:
                continue
            row = ensure_player(db, pid, player)
            if incident_class in {"yellow", "yellowcard"}:
                row["yellow_cards"] += 1
            if incident_class in {"red", "yellowred", "redcard"}:
                row["red_cards"] += 1

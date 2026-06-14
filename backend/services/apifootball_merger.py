from __future__ import annotations

from typing import Any

from .apifootball_advanced_utils import fixture_id, fixture_label, safe_float, safe_int


def player_key(player: dict[str, Any], team_name: str | None = None) -> str:
    player_id = player.get("id")
    if player_id is not None:
        return str(player_id)
    name = player.get("name") or player.get("firstname") or "Jugador"
    return f"{name}|{team_name or ''}".lower()


def ensure_player(db: dict[str, dict[str, Any]], player: dict[str, Any], team: dict[str, Any] | None = None) -> dict[str, Any]:
    team = team or {}
    team_name = team.get("name")
    key = player_key(player, team_name)
    row = db.setdefault(
        key,
        {
            "player_id": player.get("id"),
            "player": player.get("name") or player.get("firstname") or "Jugador",
            "team": team_name,
            "team_id": team.get("id"),
            "position": None,
            "age": None,
            "date_of_birth": None,
            "minutes_played": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "fouls_committed": 0,
            "was_fouled": 0,
            "saves": 0,
            "offsides": 0,
            "substituted_out": 0,
            "penalties_saved": 0,
            "best_rating": 0.0,
            "rating_count": 0,
            "_event_yellow_cards": 0,
            "_event_red_cards": 0,
        },
    )
    row["player_id"] = row.get("player_id") or player.get("id")
    row["player"] = row.get("player") or player.get("name") or player.get("firstname") or "Jugador"
    row["team"] = row.get("team") or team_name
    row["team_id"] = row.get("team_id") or team.get("id")
    if player.get("age") is not None:
        row["age"] = player.get("age")
    birth = player.get("birth") or {}
    if isinstance(birth, dict) and birth.get("date"):
        row["date_of_birth"] = birth.get("date")
    return row


def merge_stat(row: dict[str, Any], stat: dict[str, Any]) -> None:
    games = stat.get("games") or {}
    cards = stat.get("cards") or {}
    fouls = stat.get("fouls") or {}
    goals = stat.get("goals") or {}
    penalty = stat.get("penalty") or {}

    row["position"] = row.get("position") or games.get("position")
    row["minutes_played"] += safe_int(games.get("minutes"))
    row["yellow_cards"] += safe_int(cards.get("yellow"))
    row["red_cards"] += safe_int(cards.get("red"))
    row["fouls_committed"] += safe_int(fouls.get("committed"))
    row["was_fouled"] += safe_int(fouls.get("drawn"))
    row["saves"] += safe_int(goals.get("saves"))
    row["offsides"] += safe_int(stat.get("offsides"))
    row["penalties_saved"] += safe_int(penalty.get("saved"))

    rating = safe_float(games.get("rating"))
    if rating > 0:
        row["best_rating"] = max(safe_float(row.get("best_rating")), rating)
        row["rating_count"] += 1


def merge_season_players(db: dict[str, dict[str, Any]], players_payload: list[dict[str, Any]]) -> None:
    for item in players_payload:
        player = item.get("player") or {}
        for stat in item.get("statistics") or []:
            row = ensure_player(db, player, stat.get("team") or {})
            merge_stat(row, stat)


def merge_fixture_player_stats(
    db: dict[str, dict[str, Any]],
    fixture_players: dict[str, Any],
    fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    best_players: list[dict[str, Any]] = []
    fixtures_by_id = {fixture_id(f): f for f in fixtures if fixture_id(f)}

    for fid, team_entries in (fixture_players or {}).items():
        match_label = fixture_label(fixtures_by_id.get(str(fid), {})) if str(fid) in fixtures_by_id else f"Fixture {fid}"
        best: dict[str, Any] | None = None
        for team_entry in team_entries or []:
            team = team_entry.get("team") or {}
            for player_entry in team_entry.get("players") or []:
                player = player_entry.get("player") or {}
                row = ensure_player(db, player, team)
                for stat in player_entry.get("statistics") or []:
                    merge_stat(row, stat)
                    rating = safe_float((stat.get("games") or {}).get("rating"))
                    if rating > 0 and (best is None or rating > safe_float(best.get("rating"))):
                        best = {
                            "fixture_id": fid,
                            "match": match_label,
                            "player": row.get("player"),
                            "team": row.get("team"),
                            "rating": rating,
                        }
        if best:
            best_players.append(best)
    best_players.sort(key=lambda row: (-safe_float(row.get("rating")), str(row.get("match") or "")))
    return best_players


def merge_events(db: dict[str, dict[str, Any]], events_by_fixture: dict[str, Any]) -> None:
    for events in events_by_fixture.values():
        for event in events or []:
            event_type = str(event.get("type") or "").lower()
            detail = str(event.get("detail") or "").lower()
            team = event.get("team") or {}
            player = event.get("player") or {}
            assist = event.get("assist") or {}

            if event_type == "card" and player.get("name"):
                row = ensure_player(db, player, team)
                if "yellow" in detail:
                    row["_event_yellow_cards"] += 1
                if "red" in detail:
                    row["_event_red_cards"] += 1

            if event_type in {"subst", "substitution"}:
                player_out = assist if assist.get("name") else player
                if player_out.get("name"):
                    row = ensure_player(db, player_out, team)
                    row["substituted_out"] += 1


def finalize_rows(db: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in db.values():
        row["yellow_cards"] = max(safe_int(row.get("yellow_cards")), safe_int(row.get("_event_yellow_cards")))
        row["red_cards"] = max(safe_int(row.get("red_cards")), safe_int(row.get("_event_red_cards")))
        row.pop("_event_yellow_cards", None)
        row.pop("_event_red_cards", None)
        rows.append(row)
    rows.sort(key=lambda r: str(r.get("player") or ""))
    return rows

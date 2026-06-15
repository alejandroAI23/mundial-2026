from __future__ import annotations

import argparse
import csv
import logging
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

JUGADORES_CSV = DATA_DIR / "jugadores_stats.csv"
PORTEROS_CSV = DATA_DIR / "porteros_stats.csv"
MOTM_CSV = DATA_DIR / "partidos_motm.csv"
DISCIPLINA_CSV = DATA_DIR / "disciplina.csv"
MATCHES_CSV = DATA_DIR / "sofascore_matches.csv"
BASE_URL = "https://www.sofascore.com/api/v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.sofascore.com/",
    "Origin": "https://www.sofascore.com",
}

JUGADORES_HEADER = ["partido_id", "match_id", "fecha", "jugador_id", "jugador", "pais", "rival", "posicion", "titular", "minutos", "goles", "asistencias", "disparos", "tiros_puerta", "pases_clave", "regates_exitosos", "faltas_cometidas", "faltas_recibidas", "fueras_juego", "rating", "fecha_nacimiento", "fuente", "actualizado_en", "es_ejemplo"]
PORTEROS_HEADER = ["partido_id", "match_id", "fecha", "portero_id", "portero", "pais", "rival", "titular", "minutos", "saves", "saves_area", "goles_encajados", "porterias_cero", "penaltis_parados", "rating", "fuente", "actualizado_en", "es_ejemplo"]
MOTM_HEADER = ["partido_id", "match_id", "fecha", "local", "visitante", "jugador_id", "jugador", "pais", "rating", "criterio", "fuente", "actualizado_en", "es_ejemplo"]
DISCIPLINA_HEADER = ["partido_id", "match_id", "fecha", "jugador_id", "jugador", "pais", "rival", "amarillas", "segundas_amarillas", "rojas", "faltas_cometidas", "faltas_recibidas", "fuente", "actualizado_en", "es_ejemplo"]


class SofaScoreBlocked(RuntimeError):
    pass


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"scraper_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", "null"):
            return default
        return int(float(value))
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, "", "null"):
            return default
        return float(value)
    except Exception:
        return default


def get_json(path: str, retries: int = 3) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            time.sleep(random.uniform(1.0, 3.0))
            response = requests.get(url, headers=HEADERS, timeout=25)
            body = response.text[:180]
            if response.status_code == 403 and "challenge" in body.lower():
                raise SofaScoreBlocked(f"SofaScore bloquea la llamada con 403 challenge en {path}")
            if response.status_code in {403, 429, 500, 502, 503, 504}:
                raise RuntimeError(f"HTTP {response.status_code}: {body}")
            response.raise_for_status()
            return response.json()
        except SofaScoreBlocked:
            raise
        except Exception as exc:
            last_exc = exc
            logging.warning("Intento %s/%s fallido para %s: %s", attempt, retries, path, exc)
            time.sleep(random.uniform(2.0, 6.0))
    raise RuntimeError(f"No se pudo descargar {path}: {last_exc}")


def ensure_csv(path: Path, header: list[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=header).writeheader()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_dedup(path: Path, header: list[str], rows: list[dict[str, Any]], key_fields: list[str]) -> int:
    ensure_csv(path, header)
    old_rows = read_rows(path)
    seen = {tuple(str(row.get(k, "")) for k in key_fields) for row in old_rows}
    new_rows = []
    for row in rows:
        clean = {field: row.get(field, "") for field in header}
        key = tuple(str(clean.get(k, "")) for k in key_fields)
        if key not in seen:
            seen.add(key)
            new_rows.append(clean)
    if new_rows:
        with path.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=header).writerows(new_rows)
    return len(new_rows)


def player_name(player: dict[str, Any]) -> str:
    return player.get("name") or player.get("shortName") or player.get("slug") or "Jugador"


def team_name(team: dict[str, Any]) -> str:
    return team.get("name") or team.get("shortName") or ""


def extract_event_info(match_id: int, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    fallback = fallback or {}
    try:
        event = get_json(f"/event/{match_id}").get("event") or {}
    except SofaScoreBlocked:
        logging.warning("No se pudo leer /event/%s por challenge. Uso datos manuales del CSV.", match_id)
        event = {}
    home = event.get("homeTeam") or {}
    away = event.get("awayTeam") or {}
    start_ts = event.get("startTimestamp")
    fecha = fallback.get("fecha") or ""
    if start_ts:
        fecha = datetime.fromtimestamp(int(start_ts), timezone.utc).date().isoformat()
    return {"partido_id": fallback.get("partido_id") or str(match_id), "match_id": str(match_id), "fecha": fecha, "local": fallback.get("local") or team_name(home), "visitante": fallback.get("visitante") or team_name(away)}


def extract_lineup_rows(match_id: int, meta: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = get_json(f"/event/{match_id}/lineups")
    rows_players: list[dict[str, Any]] = []
    rows_goalkeepers: list[dict[str, Any]] = []
    for side_key in ("home", "away"):
        side = payload.get(side_key) or {}
        team = meta["local"] if side_key == "home" else meta["visitante"]
        rival = meta["visitante"] if side_key == "home" else meta["local"]
        for item in side.get("players") or []:
            player = item.get("player") or {}
            stats = item.get("statistics") or {}
            position = item.get("position") or player.get("position") or ""
            base = {"partido_id": meta["partido_id"], "match_id": str(match_id), "fecha": meta["fecha"], "jugador_id": player.get("id", ""), "jugador": player_name(player), "pais": team, "rival": rival, "posicion": position, "titular": not item.get("substitute", False), "minutos": safe_int(stats.get("minutesPlayed") or stats.get("minutes")), "goles": safe_int(stats.get("goals")), "asistencias": safe_int(stats.get("goalAssist") or stats.get("assists")), "disparos": safe_int(stats.get("totalShots") or stats.get("shots")), "tiros_puerta": safe_int(stats.get("shotsOnTarget")), "pases_clave": safe_int(stats.get("keyPass")), "regates_exitosos": safe_int(stats.get("successfulDribbles")), "faltas_cometidas": safe_int(stats.get("fouls")), "faltas_recibidas": safe_int(stats.get("wasFouled")), "fueras_juego": safe_int(stats.get("offsides")), "rating": safe_float(stats.get("rating")), "fecha_nacimiento": player.get("dateOfBirthTimestamp", ""), "fuente": "sofascore", "actualizado_en": now_iso(), "es_ejemplo": "false"}
            rows_players.append(base)
            is_gk = str(position).upper() in {"G", "GK"} or "goalkeeper" in str(position).lower()
            if is_gk:
                rows_goalkeepers.append({"partido_id": meta["partido_id"], "match_id": str(match_id), "fecha": meta["fecha"], "portero_id": player.get("id", ""), "portero": player_name(player), "pais": team, "rival": rival, "titular": base["titular"], "minutos": base["minutos"], "saves": safe_int(stats.get("saves") or stats.get("goalkeeperSaves")), "saves_area": safe_int(stats.get("savedShotsFromInsideTheBox")), "goles_encajados": safe_int(stats.get("goalsConceded")), "porterias_cero": 1 if safe_int(stats.get("goalsConceded")) == 0 and base["minutos"] > 0 else 0, "penaltis_parados": safe_int(stats.get("penaltySave") or stats.get("penaltySaves")), "rating": base["rating"], "fuente": "sofascore", "actualizado_en": now_iso(), "es_ejemplo": "false"})
    return rows_players, rows_goalkeepers


def extract_discipline_rows(match_id: int, meta: dict[str, Any], player_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in player_rows:
        key = str(row.get("jugador_id") or row.get("jugador"))
        output[key] = {"partido_id": row["partido_id"], "match_id": row["match_id"], "fecha": row["fecha"], "jugador_id": row["jugador_id"], "jugador": row["jugador"], "pais": row["pais"], "rival": row["rival"], "amarillas": 0, "segundas_amarillas": 0, "rojas": 0, "faltas_cometidas": row.get("faltas_cometidas", 0), "faltas_recibidas": row.get("faltas_recibidas", 0), "fuente": "sofascore", "actualizado_en": now_iso(), "es_ejemplo": "false"}
    incidents = get_json(f"/event/{match_id}/incidents").get("incidents") or []
    for inc in incidents:
        incident_class = str(inc.get("incidentClass") or "").lower()
        if incident_class not in {"yellow", "red", "yellowred"}:
            continue
        player = inc.get("player") or {}
        key = str(player.get("id") or player_name(player))
        row = output.setdefault(key, {"partido_id": meta["partido_id"], "match_id": str(match_id), "fecha": meta["fecha"], "jugador_id": player.get("id", ""), "jugador": player_name(player), "pais": "", "rival": "", "amarillas": 0, "segundas_amarillas": 0, "rojas": 0, "faltas_cometidas": 0, "faltas_recibidas": 0, "fuente": "sofascore", "actualizado_en": now_iso(), "es_ejemplo": "false"})
        if incident_class == "yellow": row["amarillas"] = safe_int(row["amarillas"]) + 1
        if incident_class == "yellowred": row["segundas_amarillas"] = safe_int(row["segundas_amarillas"]) + 1; row["rojas"] = safe_int(row["rojas"]) + 1
        if incident_class == "red": row["rojas"] = safe_int(row["rojas"]) + 1
    return list(output.values())


def extract_motm_row(match_id: int, meta: dict[str, Any], player_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    rated = [row for row in player_rows if safe_float(row.get("rating")) > 0]
    if not rated:
        return None
    top = sorted(rated, key=lambda row: safe_float(row.get("rating")), reverse=True)[0]
    return {"partido_id": meta["partido_id"], "match_id": str(match_id), "fecha": meta["fecha"], "local": meta.get("local", ""), "visitante": meta.get("visitante", ""), "jugador_id": top.get("jugador_id", ""), "jugador": top.get("jugador", ""), "pais": top.get("pais", ""), "rating": top.get("rating", ""), "criterio": "rating_mas_alto_sofascore", "fuente": "sofascore", "actualizado_en": now_iso(), "es_ejemplo": "false"}


def scrape_match(match_id: int, fallback: dict[str, Any] | None = None) -> bool:
    logging.info("Procesando match_id=%s", match_id)
    try:
        meta = extract_event_info(match_id, fallback)
        player_rows, goalkeeper_rows = extract_lineup_rows(match_id, meta)
        discipline_rows = extract_discipline_rows(match_id, meta, player_rows)
        motm_row = extract_motm_row(match_id, meta, player_rows)
        logging.info("Añadidos: jugadores=%s porteros=%s disciplina=%s motm=%s", append_dedup(JUGADORES_CSV, JUGADORES_HEADER, player_rows, ["match_id", "jugador_id"]), append_dedup(PORTEROS_CSV, PORTEROS_HEADER, goalkeeper_rows, ["match_id", "portero_id"]), append_dedup(DISCIPLINA_CSV, DISCIPLINA_HEADER, discipline_rows, ["match_id", "jugador_id"]), append_dedup(MOTM_CSV, MOTM_HEADER, [motm_row] if motm_row else [], ["match_id"]))
        return True
    except SofaScoreBlocked as exc:
        logging.error("BLOQUEADO match_id=%s: %s. Rellena los CSV manualmente o prueba desde local.", match_id, exc)
        return False
    except Exception as exc:
        logging.exception("ERROR match_id=%s: %s", match_id, exc)
        return False


def all_played_matches() -> list[dict[str, Any]]:
    rows = read_rows(MATCHES_CSV)
    return [row for row in rows if str(row.get("es_ejemplo", "")).lower() != "true" and str(row.get("estado", "")).lower() in {"finalizado", "played", "ft", "finished"} and row.get("match_id")]


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper ligero SofaScore para estadísticas del Mundial 2026")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--match-id", type=int)
    group.add_argument("--all-played", action="store_true")
    args = parser.parse_args()
    setup_logging()
    for path, header in [(JUGADORES_CSV, JUGADORES_HEADER), (PORTEROS_CSV, PORTEROS_HEADER), (MOTM_CSV, MOTM_HEADER), (DISCIPLINA_CSV, DISCIPLINA_HEADER)]:
        ensure_csv(path, header)
    if args.match_id:
        ok = scrape_match(args.match_id)
        logging.info("Resumen scraper: ok=%s fallidos=%s", 1 if ok else 0, 0 if ok else 1)
        return
    rows = all_played_matches()
    ok_count = 0
    fail_count = 0
    for row in rows:
        if scrape_match(int(row["match_id"]), row):
            ok_count += 1
        else:
            fail_count += 1
    logging.info("Resumen scraper: partidos=%s ok=%s fallidos=%s", len(rows), ok_count, fail_count)
    logging.info("El workflow termina en verde aunque SofaScore bloquee. Si fallidos > 0, usa carga manual en CSV.")


if __name__ == "__main__":
    main()

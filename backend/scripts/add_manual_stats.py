from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

JUGADORES = DATA_DIR / "jugadores_stats.csv"
PORTEROS = DATA_DIR / "porteros_stats.csv"
MOTM = DATA_DIR / "partidos_motm.csv"
DISCIPLINA = DATA_DIR / "disciplina.csv"

JUGADORES_HEADER = ["partido_id","match_id","fecha","jugador_id","jugador","pais","rival","posicion","titular","minutos","goles","asistencias","disparos","tiros_puerta","pases_clave","regates_exitosos","faltas_cometidas","faltas_recibidas","fueras_juego","rating","fecha_nacimiento","fuente","actualizado_en","es_ejemplo"]
PORTEROS_HEADER = ["partido_id","match_id","fecha","portero_id","portero","pais","rival","titular","minutos","saves","saves_area","goles_encajados","porterias_cero","penaltis_parados","rating","fuente","actualizado_en","es_ejemplo"]
MOTM_HEADER = ["partido_id","match_id","fecha","local","visitante","jugador_id","jugador","pais","rating","criterio","fuente","actualizado_en","es_ejemplo"]
DISCIPLINA_HEADER = ["partido_id","match_id","fecha","jugador_id","jugador","pais","rival","amarillas","segundas_amarillas","rojas","faltas_cometidas","faltas_recibidas","fuente","actualizado_en","es_ejemplo"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def value(data: dict[str, Any], key: str, default: Any = "") -> Any:
    item = data.get(key, default)
    return default if item is None else item


def ensure(path: Path, header: list[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=header).writeheader()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def upsert(path: Path, header: list[str], row: dict[str, Any], keys: list[str]) -> str:
    ensure(path, header)
    rows = read_rows(path)
    clean = {field: str(row.get(field, "")) for field in header}
    target = tuple(clean.get(k, "") for k in keys)
    action = "inserted"
    output: list[dict[str, str]] = []
    replaced = False
    for old in rows:
        current = tuple(str(old.get(k, "")) for k in keys)
        if current == target:
            output.append(clean)
            replaced = True
            action = "updated"
        else:
            output.append({field: old.get(field, "") for field in header})
    if not replaced:
        output.append(clean)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(output)
    return action


def parse_bool(item: Any) -> bool:
    return str(item).strip().lower() in {"true", "1", "si", "sí", "yes", "y"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga guiada de estadisticas avanzadas en CSV")
    parser.add_argument("--partido-id", required=True)
    parser.add_argument("--match-id", required=True)
    parser.add_argument("--fecha", required=True)
    parser.add_argument("--local", required=True)
    parser.add_argument("--visitante", required=True)
    parser.add_argument("--jugador", required=True)
    parser.add_argument("--pais", required=True)
    parser.add_argument("--rival", required=True)
    parser.add_argument("--stats-json", required=True)
    args = parser.parse_args()

    stats = json.loads(args.stats_json or "{}")
    jugador_id = value(stats, "jugador_id", "")
    updated = now()

    common = {
        "partido_id": args.partido_id,
        "match_id": args.match_id,
        "fecha": args.fecha,
        "jugador_id": jugador_id,
        "jugador": args.jugador,
        "pais": args.pais,
        "rival": args.rival,
        "fuente": "manual_form",
        "actualizado_en": updated,
        "es_ejemplo": "false",
    }

    player_row = {
        **common,
        "posicion": value(stats, "posicion", ""),
        "titular": str(parse_bool(value(stats, "titular", True))).lower(),
        "minutos": value(stats, "minutos", 0),
        "goles": value(stats, "goles", 0),
        "asistencias": value(stats, "asistencias", 0),
        "disparos": value(stats, "disparos", 0),
        "tiros_puerta": value(stats, "tiros_puerta", 0),
        "pases_clave": value(stats, "pases_clave", 0),
        "regates_exitosos": value(stats, "regates_exitosos", 0),
        "faltas_cometidas": value(stats, "faltas_cometidas", 0),
        "faltas_recibidas": value(stats, "faltas_recibidas", 0),
        "fueras_juego": value(stats, "fueras_juego", 0),
        "rating": value(stats, "rating", 0),
        "fecha_nacimiento": value(stats, "fecha_nacimiento", ""),
    }
    player_action = upsert(JUGADORES, JUGADORES_HEADER, player_row, ["match_id", "jugador"])

    disc_row = {
        **common,
        "amarillas": value(stats, "amarillas", 0),
        "segundas_amarillas": value(stats, "segundas_amarillas", 0),
        "rojas": value(stats, "rojas", 0),
        "faltas_cometidas": value(stats, "faltas_cometidas", 0),
        "faltas_recibidas": value(stats, "faltas_recibidas", 0),
    }
    disc_action = upsert(DISCIPLINA, DISCIPLINA_HEADER, disc_row, ["match_id", "jugador"])

    goalkeeper_action = "skipped"
    if parse_bool(value(stats, "es_portero", False)):
        gk_row = {
            "partido_id": args.partido_id,
            "match_id": args.match_id,
            "fecha": args.fecha,
            "portero_id": jugador_id,
            "portero": args.jugador,
            "pais": args.pais,
            "rival": args.rival,
            "titular": str(parse_bool(value(stats, "titular", True))).lower(),
            "minutos": value(stats, "minutos", 0),
            "saves": value(stats, "saves", 0),
            "saves_area": value(stats, "saves_area", 0),
            "goles_encajados": value(stats, "goles_encajados", 0),
            "porterias_cero": value(stats, "porterias_cero", 0),
            "penaltis_parados": value(stats, "penaltis_parados", 0),
            "rating": value(stats, "rating", 0),
            "fuente": "manual_form",
            "actualizado_en": updated,
            "es_ejemplo": "false",
        }
        goalkeeper_action = upsert(PORTEROS, PORTEROS_HEADER, gk_row, ["match_id", "portero"])

    motm_action = "skipped"
    if parse_bool(value(stats, "motm", False)):
        motm_row = {
            "partido_id": args.partido_id,
            "match_id": args.match_id,
            "fecha": args.fecha,
            "local": args.local,
            "visitante": args.visitante,
            "jugador_id": jugador_id,
            "jugador": args.jugador,
            "pais": args.pais,
            "rating": value(stats, "rating", 0),
            "criterio": value(stats, "criterio", "manual_form"),
            "fuente": "manual_form",
            "actualizado_en": updated,
            "es_ejemplo": "false",
        }
        motm_action = upsert(MOTM, MOTM_HEADER, motm_row, ["match_id"])

    print("Resumen carga manual")
    print(f"jugadores_stats.csv: {player_action}")
    print(f"disciplina.csv: {disc_action}")
    print(f"porteros_stats.csv: {goalkeeper_action}")
    print(f"partidos_motm.csv: {motm_action}")


if __name__ == "__main__":
    main()

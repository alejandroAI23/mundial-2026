from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
JUGADORES_CSV = DATA_DIR / "jugadores_stats.csv"
PORTEROS_CSV = DATA_DIR / "porteros_stats.csv"
MOTM_CSV = DATA_DIR / "partidos_motm.csv"
DISCIPLINA_CSV = DATA_DIR / "disciplina.csv"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "es_ejemplo" in df.columns:
        df = df[df["es_ejemplo"].astype(str).str.lower() != "true"]
    return df.fillna(0)


def _top_sum(path: Path, metric: str, n: int = 5) -> list[dict[str, Any]]:
    df = _read_csv(path)
    if df.empty or metric not in df.columns:
        return []
    df[metric] = pd.to_numeric(df[metric], errors="coerce").fillna(0)
    grouped = df.groupby(["jugador", "pais"], as_index=False)[metric].sum()
    return grouped.sort_values(metric, ascending=False).head(n).to_dict("records")


def top_amarillas(n: int = 5) -> list[dict[str, Any]]:
    rows = _top_sum(DISCIPLINA_CSV, "amarillas", n)
    return [{"jugador": r["jugador"], "pais": r["pais"], "amarillas": int(r["amarillas"])} for r in rows]


def top_rojas(n: int = 5) -> list[dict[str, Any]]:
    rows = _top_sum(DISCIPLINA_CSV, "rojas", n)
    return [{"jugador": r["jugador"], "pais": r["pais"], "rojas": int(r["rojas"])} for r in rows]


def top_faltas_cometidas(n: int = 5) -> list[dict[str, Any]]:
    rows = _top_sum(DISCIPLINA_CSV, "faltas_cometidas", n)
    return [{"jugador": r["jugador"], "pais": r["pais"], "faltas_cometidas": int(r["faltas_cometidas"])} for r in rows]


def top_faltas_recibidas(n: int = 5) -> list[dict[str, Any]]:
    rows = _top_sum(DISCIPLINA_CSV, "faltas_recibidas", n)
    return [{"jugador": r["jugador"], "pais": r["pais"], "faltas_recibidas": int(r["faltas_recibidas"])} for r in rows]


def top_fueras_juego(n: int = 5) -> list[dict[str, Any]]:
    rows = _top_sum(JUGADORES_CSV, "fueras_juego", n)
    return [{"jugador": r["jugador"], "pais": r["pais"], "fueras_juego": int(r["fueras_juego"])} for r in rows]


def top_goles(n: int = 5) -> list[dict[str, Any]]:
    rows = _top_sum(JUGADORES_CSV, "goles", n)
    return [{"jugador": r["jugador"], "pais": r["pais"], "goles": int(r["goles"])} for r in rows]


def jugador_mas_joven() -> dict[str, Any]:
    df = _read_csv(JUGADORES_CSV)
    if df.empty or "fecha_nacimiento" not in df.columns:
        return {}
    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")
    df = df.dropna(subset=["fecha_nacimiento"]).sort_values("fecha_nacimiento", ascending=False)
    if df.empty:
        return {}
    row = df.iloc[0].to_dict()
    born = row["fecha_nacimiento"].date()
    days = (date.today() - born).days
    return {"jugador": row.get("jugador"), "pais": row.get("pais"), "fecha_nacimiento": born.isoformat(), "edad": f"{days // 365} años {days % 365} días"}


def top_porteros_paradas(n: int = 5) -> list[dict[str, Any]]:
    df = _read_csv(PORTEROS_CSV)
    if df.empty or "saves" not in df.columns:
        return []
    df["saves"] = pd.to_numeric(df["saves"], errors="coerce").fillna(0)
    grouped = df.groupby(["portero", "pais"], as_index=False)["saves"].sum()
    return grouped.sort_values("saves", ascending=False).head(n).to_dict("records")


def portero_menos_goleado() -> dict[str, Any]:
    df = _read_csv(PORTEROS_CSV)
    if df.empty or "goles_encajados" not in df.columns:
        return {}
    df["goles_encajados"] = pd.to_numeric(df["goles_encajados"], errors="coerce").fillna(0)
    grouped = df.groupby(["portero", "pais"], as_index=False).agg(goles_encajados=("goles_encajados", "sum"), partidos=("match_id", "count"), porterias_cero=("porterias_cero", "sum"))
    grouped = grouped.sort_values(["goles_encajados", "porterias_cero", "partidos"], ascending=[True, False, False])
    return grouped.head(1).to_dict("records")[0] if not grouped.empty else {}


def motm_historico() -> list[dict[str, Any]]:
    df = _read_csv(MOTM_CSV)
    return df.sort_values("fecha").to_dict("records") if not df.empty and "fecha" in df.columns else df.to_dict("records")


def resumen_jugador(nombre: str) -> dict[str, Any]:
    df = _read_csv(JUGADORES_CSV)
    if df.empty:
        return {}
    rows = df[df["jugador"].astype(str).str.contains(nombre, case=False, na=False)]
    if rows.empty:
        return {}
    summary = {"jugador": rows.iloc[0]["jugador"], "pais": rows.iloc[0]["pais"], "partidos": int(rows["match_id"].nunique())}
    for column in ["minutos", "goles", "asistencias", "faltas_cometidas", "faltas_recibidas", "fueras_juego"]:
        if column in rows.columns:
            summary[column] = int(pd.to_numeric(rows[column], errors="coerce").fillna(0).sum())
    disc = _read_csv(DISCIPLINA_CSV)
    if not disc.empty:
        d = disc[disc["jugador"].astype(str).str.contains(nombre, case=False, na=False)]
        for column in ["amarillas", "segundas_amarillas", "rojas"]:
            if column in d.columns:
                summary[column] = int(pd.to_numeric(d[column], errors="coerce").fillna(0).sum())
    return summary

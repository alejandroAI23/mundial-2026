from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.data_store import load_data, save_data, csv_paths
from services.qa_service import answer_question
from services.stats_service import build_prediction, update_all_data

APP_NAME = os.getenv("APP_NAME", "Mundial 2026 IA API")
AUTO_SYNC_ON_STARTUP = os.getenv("AUTO_SYNC_ON_STARTUP", "false").lower() == "true"

app = FastAPI(title=APP_NAME, version="1.0.0")

origins = [
    "https://alejandroai23.github.io",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
]
extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA: dict[str, Any] = load_data()


class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class PredictionRequest(BaseModel):
    team_a: str = Field(..., min_length=1)
    team_b: str = Field(..., min_length=1)


@app.on_event("startup")
def startup() -> None:
    global DATA
    if AUTO_SYNC_ON_STARTUP:
        try:
            DATA = update_all_data()
            save_data(DATA)
        except Exception:
            # Keep bundled JSON as fallback.
            DATA = load_data()


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": APP_NAME,
        "status": "ok",
        "docs": "/docs",
        "endpoints": [
            "/api/clasificacion",
            "/api/goleadores",
            "/api/partidos",
            "/api/equipos",
            "/api/estadios",
            "/api/qa",
            "/api/prediccion",
            "/api/sync",
        ],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/clasificacion")
def clasificacion(grupo: str | None = None) -> list[dict[str, Any]]:
    rows = DATA.get("classification", []) or []
    if grupo:
        rows = [r for r in rows if str(r.get("group", "")).upper() == grupo.upper()]
    return rows


@app.get("/api/goleadores")
def goleadores(limit: int = 50) -> list[dict[str, Any]]:
    rows = DATA.get("top_scorers", []) or []
    rows = sorted(rows, key=lambda r: int(r.get("goals") or 0), reverse=True)
    return rows[: max(1, min(limit, 200))]


@app.get("/api/partidos")
def partidos() -> list[dict[str, Any]]:
    return DATA.get("matches", []) or []


@app.get("/api/equipos")
def equipos() -> list[dict[str, Any]]:
    return DATA.get("teams", []) or []


@app.get("/api/estadios")
def estadios() -> list[dict[str, Any]]:
    return DATA.get("stadiums", []) or []


@app.get("/api/metadata")
def metadata() -> dict[str, Any]:
    return {"metadata": DATA.get("metadata", {}), "files": csv_paths()}


@app.post("/api/sync")
def sync() -> dict[str, Any]:
    global DATA
    try:
        DATA = update_all_data()
        save_data(DATA)
        return {
            "status": "ok",
            "metadata": DATA.get("metadata", {}),
            "classification_rows": len(DATA.get("classification", [])),
            "top_scorers_rows": len(DATA.get("top_scorers", [])),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo sincronizar con la API externa: {exc}") from exc


@app.post("/api/qa")
def qa(request: QARequest) -> dict[str, Any]:
    return answer_question(request.question, DATA)


@app.post("/api/prediccion")
def prediccion(request: PredictionRequest) -> dict[str, Any]:
    return build_prediction(DATA.get("classification", []) or [], request.team_a, request.team_b)

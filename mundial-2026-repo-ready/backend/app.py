"""API FastAPI para Mundial 2026: datos + IA ligera.

Ejecución local:
    pip install -r requirements.txt
    python scripts/update_data.py
    uvicorn app:app --reload
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.qa_service import answer_question
from services.stats_service import load_local_data
from services.update_service import refresh_worldcup_data

app = FastAPI(title="Mundial 2026 AI API", version="1.0.0")

# Ajusta allow_origins cuando tengas tu URL final de Replit/Render y GitHub Pages.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5500",
        "https://alejandroai23.github.io",
        "https://alejandroai23.github.io/mundial-2026",
    ],
    allow_origin_regex=r"https://.*\.github\.io",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QARequest(BaseModel):
    question: str
    use_local_model: bool = False


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "Mundial 2026 AI API",
        "status": "ok",
        "endpoints": [
            "/api/clasificacion",
            "/api/goleadores",
            "/api/partidos",
            "/api/equipos",
            "/api/estadios",
            "/api/qa",
            "/api/sync",
        ],
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/sync")
def sync() -> dict[str, Any]:
    """Sincroniza API externa -> data/worldcup_data.json + CSV.

    En producción puedes proteger este endpoint con una clave simple o ejecutarlo
    manualmente desde la consola para evitar abusos.
    """
    try:
        return refresh_worldcup_data()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error sincronizando datos: {exc}") from exc


@app.get("/api/data")
def data() -> dict[str, Any]:
    return load_local_data()


@app.get("/api/clasificacion")
def clasificacion() -> list[dict[str, Any]]:
    return load_local_data().get("classification", [])


@app.get("/api/goleadores")
def goleadores() -> list[dict[str, Any]]:
    return load_local_data().get("top_scorers", [])


@app.get("/api/partidos")
def partidos() -> list[dict[str, Any]]:
    return load_local_data().get("games", [])


@app.get("/api/equipos")
def equipos() -> list[dict[str, Any]]:
    return load_local_data().get("teams", [])


@app.get("/api/estadios")
def estadios() -> list[dict[str, Any]]:
    return load_local_data().get("stadiums", [])


@app.post("/api/qa")
def qa(request: QARequest) -> dict[str, Any]:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")
    data = load_local_data()
    # Primera capa: reglas con datos estructurados. Más fiable y gratis.
    answer = answer_question(question, data)

    # Segunda capa opcional: modelo local. Solo si lo pides y está configurado.
    if request.use_local_model and answer.get("confidence", 0) < 0.78:
        try:
            from llm.local_llm import generate_with_context
            context = build_context_for_llm(data)
            llm_answer = generate_with_context(question, context)
            if llm_answer:
                return {"answer": llm_answer, "source": "local_llm", "confidence": 0.7}
        except Exception as exc:
            answer["local_model_error"] = str(exc)
    return answer


def build_context_for_llm(data: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("CLASIFICACIÓN:")
    for r in data.get("classification", [])[:60]:
        lines.append(f"{r.get('team')} | Grupo {r.get('group')} | {r.get('points')} puntos | GF {r.get('goals_for')} | GC {r.get('goals_against')}")
    lines.append("\nGOLEADORES:")
    for r in data.get("top_scorers", [])[:40]:
        lines.append(f"{r.get('player')} | {r.get('team')} | {r.get('goals')} goles")
    return "\n".join(lines)

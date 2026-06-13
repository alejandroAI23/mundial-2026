"""Genera dataset JSONL de entrenamiento desde CSV del Mundial 2026.

Este dataset sirve para afinar un modelo pequeño. Para una primera versión,
usa el endpoint /api/qa con reglas; el fine-tuning es fase 2.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "backend" / "data"
OUT = Path(__file__).resolve().parents[1] / "datasets" / "qa_worldcup_generated.jsonl"


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    classification = load_csv(DATA_DIR / "worldcup_classification.csv")
    scorers = load_csv(DATA_DIR / "worldcup_top_scorers.csv")
    examples: list[dict[str, str]] = []

    for row in classification:
        team = row.get("team")
        group = row.get("group")
        points = row.get("points")
        if not team:
            continue
        examples.append({"question": f"¿Cuántos puntos tiene {team}?", "answer": f"{team} tiene {points} puntos en el Grupo {group}."})
        examples.append({"question": f"¿En qué grupo está {team}?", "answer": f"{team} está en el Grupo {group}."})

    groups = sorted({r.get("group", "") for r in classification if r.get("group")})
    for group in groups:
        rows = [r for r in classification if r.get("group") == group]
        rows.sort(key=lambda r: (int(r.get("points") or 0), int(r.get("goal_difference") or 0), int(r.get("goals_for") or 0)), reverse=True)
        if rows:
            leader = rows[0]
            examples.append({"question": f"¿Quién lidera el grupo {group}?", "answer": f"El líder del Grupo {group} es {leader.get('team')} con {leader.get('points')} puntos."})

    if scorers:
        scorers.sort(key=lambda r: int(r.get("goals") or 0), reverse=True)
        top = scorers[0]
        examples.append({"question": "¿Quién es el máximo goleador?", "answer": f"El máximo goleador es {top.get('player')} de {top.get('team')} con {top.get('goals')} goles."})
        for row in scorers[:20]:
            examples.append({"question": f"¿Cuántos goles lleva {row.get('player')}?", "answer": f"{row.get('player')} lleva {row.get('goals')} goles con {row.get('team')}."})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Generados {len(examples)} ejemplos en {OUT}")


if __name__ == "__main__":
    main()

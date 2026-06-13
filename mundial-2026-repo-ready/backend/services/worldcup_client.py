"""Cliente HTTP para la API libre World Cup 2026.

Fuente principal prevista:
- https://worldcup26.ir/get/games
- https://worldcup26.ir/get/groups
- https://worldcup26.ir/get/teams
- https://worldcup26.ir/get/stadiums

El cliente está pensado para backend, no para GitHub Pages directamente, así evitamos
problemas de CORS y podemos cachear datos en JSON/CSV.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class WorldCupClientConfig:
    base_url: str = "https://worldcup26.ir/get"
    timeout_seconds: int = 25


class WorldCupClient:
    def __init__(self, config: WorldCupClientConfig | None = None) -> None:
        self.config = config or WorldCupClientConfig()

    def _get(self, endpoint: str) -> dict[str, Any] | list[Any]:
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.get(url, timeout=self.config.timeout_seconds)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _unwrap(payload: dict[str, Any] | list[Any], *keys: str) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        # Último recurso: primera lista de diccionarios que encontremos
        for value in payload.values():
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    def games(self) -> list[dict[str, Any]]:
        return self._unwrap(self._get("games"), "games", "matches")

    def groups(self) -> list[dict[str, Any]]:
        return self._unwrap(self._get("groups"), "groups")

    def teams(self) -> list[dict[str, Any]]:
        return self._unwrap(self._get("teams"), "teams")

    def stadiums(self) -> list[dict[str, Any]]:
        return self._unwrap(self._get("stadiums"), "stadiums")

    def all_data(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "games": self.games(),
            "groups": self.groups(),
            "teams": self.teams(),
            "stadiums": self.stadiums(),
        }

from __future__ import annotations

import os
from typing import Any

import requests


API_BASE_URL = os.getenv("WORLDCUP_API_BASE_URL", "https://worldcup26.ir/get").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))


def _unwrap(data: Any, *keys: str) -> Any:
    if isinstance(data, dict):
        for key in keys:
            if key in data:
                return data[key]
    return data


def fetch_endpoint(endpoint: str) -> Any:
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_games() -> list[dict[str, Any]]:
    data = fetch_endpoint("games")
    data = _unwrap(data, "games", "matches", "data")
    return data if isinstance(data, list) else []


def get_teams() -> list[dict[str, Any]]:
    data = fetch_endpoint("teams")
    data = _unwrap(data, "teams", "data")
    return data if isinstance(data, list) else []


def get_groups() -> Any:
    data = fetch_endpoint("groups")
    return _unwrap(data, "groups", "data")


def get_stadiums() -> list[dict[str, Any]]:
    data = fetch_endpoint("stadiums")
    data = _unwrap(data, "stadiums", "data")
    return data if isinstance(data, list) else []

from __future__ import annotations

import os
from typing import Any

import requests

BASE = os.getenv("BALLDONTLIE_BASE_URL", "https://api.balldontlie.io/fifa/worldcup/v1").rstrip("/")
TOKEN = os.getenv("BALLDONTLIE_API_KEY", "").strip()
TIMEOUT = int(os.getenv("BALLDONTLIE_REQUEST_TIMEOUT", os.getenv("REQUEST_TIMEOUT", "25")))
PER_PAGE = min(100, max(1, int(os.getenv("BALLDONTLIE_PER_PAGE", "100"))))
MAX_PAGES = max(1, int(os.getenv("BALLDONTLIE_MAX_PAGES", "50")))
HEADER_NAME = "Authori" + "zation"


class BalldontlieConfigError(RuntimeError):
    pass


class BalldontlieAPIError(RuntimeError):
    pass


class ApiKeyAuth(requests.auth.AuthBase):
    def __call__(self, request):
        request.headers[HEADER_NAME] = TOKEN
        return request


def is_balldontlie_configured() -> bool:
    return bool(TOKEN)


def fetch_paginated(endpoint: str, params: dict[str, Any] | None = None, max_pages: int = MAX_PAGES) -> list[dict[str, Any]]:
    if not TOKEN:
        raise BalldontlieConfigError("BALLDONTLIE_API_KEY no está configurada.")
    query = dict(params or {})
    query.setdefault("per_page", PER_PAGE)
    rows: list[dict[str, Any]] = []
    cursor = query.get("cursor")
    for _ in range(max_pages):
        if cursor:
            query["cursor"] = cursor
        try:
            response = requests.get(f"{BASE}/{endpoint.lstrip('/')}", auth=ApiKeyAuth(), params=query, timeout=TIMEOUT)
            if response.status_code == 401:
                raise BalldontlieAPIError("BALLDONTLIE devuelve 401. Revisa clave y tier para endpoints avanzados.")
            if response.status_code == 429:
                raise BalldontlieAPIError("BALLDONTLIE devuelve 429: límite de peticiones alcanzado.")
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise BalldontlieAPIError(f"Error llamando a BALLDONTLIE {endpoint}: {exc}") from exc
        data = payload.get("data", []) if isinstance(payload, dict) else []
        rows.extend([item for item in data if isinstance(item, dict)])
        meta = payload.get("meta", {}) if isinstance(payload, dict) and isinstance(payload.get("meta"), dict) else {}
        cursor = meta.get("next_cursor")
        if not cursor:
            break
    return rows

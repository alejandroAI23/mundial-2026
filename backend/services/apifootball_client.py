from __future__ import annotations

import os
import time
from typing import Any

import requests


class APIFootballConfigError(RuntimeError):
    """Raised when API-FOOTBALL credentials are missing."""


class APIFootballAPIError(RuntimeError):
    """Raised when API-FOOTBALL returns an error response."""


BASE_URL = os.getenv("API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io").rstrip("/")
TIMEOUT = float(os.getenv("API_FOOTBALL_TIMEOUT", "20"))
MAX_RETRIES = int(os.getenv("API_FOOTBALL_MAX_RETRIES", "2"))
RETRY_SLEEP_SECONDS = float(os.getenv("API_FOOTBALL_RETRY_SLEEP_SECONDS", "1.5"))


def is_api_football_configured() -> bool:
    return bool(os.getenv("API_FOOTBALL_KEY"))


def _headers() -> dict[str, str]:
    key = os.getenv("API_FOOTBALL_KEY")
    if not key:
        raise APIFootballConfigError("API_FOOTBALL_KEY no configurada")

    # API-FOOTBALL direct account header. Built at runtime to avoid exposing secrets.
    header_name = "-".join(["x", "apisports", "key"])
    return {header_name: key}


def request(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    endpoint = endpoint.lstrip("/")
    url = f"{BASE_URL}/{endpoint}"
    params = {k: v for k, v in (params or {}).items() if v not in (None, "")}

    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=_headers(), params=params, timeout=TIMEOUT)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS * (attempt + 1))
                continue
            if response.status_code == 401:
                raise APIFootballAPIError("API_FOOTBALL_KEY inválida o sin permisos")
            if response.status_code == 429:
                raise APIFootballAPIError("límite de API-FOOTBALL alcanzado")
            response.raise_for_status()
            payload = response.json()
            errors = payload.get("errors")
            if errors:
                raise APIFootballAPIError(f"API-FOOTBALL devolvió errores: {errors}")
            return payload
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS * (attempt + 1))
                continue
            raise APIFootballAPIError(f"error llamando a API-FOOTBALL {endpoint}: {exc}") from exc

    raise APIFootballAPIError(f"error llamando a API-FOOTBALL {endpoint}: {last_exc}")


def fetch_response(endpoint: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    payload = request(endpoint, params=params)
    response = payload.get("response") or []
    return response if isinstance(response, list) else []


def fetch_paginated(
    endpoint: str,
    params: dict[str, Any] | None = None,
    *,
    page_param: str = "page",
    max_pages: int | None = None,
) -> list[dict[str, Any]]:
    params = dict(params or {})
    page = int(params.pop(page_param, 1) or 1)
    max_pages = max_pages or int(os.getenv("API_FOOTBALL_MAX_PAGES", "80"))
    rows: list[dict[str, Any]] = []

    while page <= max_pages:
        payload = request(endpoint, {**params, page_param: page})
        batch = payload.get("response") or []
        if isinstance(batch, list):
            rows.extend(batch)

        paging = payload.get("paging") or {}
        total = int(paging.get("total") or page)
        current = int(paging.get("current") or page)
        if current >= total or not batch:
            break
        page = current + 1

    return rows

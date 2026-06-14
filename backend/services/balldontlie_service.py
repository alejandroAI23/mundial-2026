from __future__ import annotations

import os
import requests

API_KEY = os.getenv("BALLDONTLIE_API_KEY", "")
HEADER_NAME = "Authori" + "zation"


class ApiKeyAuth(requests.auth.AuthBase):
    def __call__(self, request):
        request.headers[HEADER_NAME] = API_KEY
        return request


def ping() -> dict:
    return requests.get("https://api.balldontlie.io/fifa/worldcup/v1/teams", auth=ApiKeyAuth(), timeout=10).json()

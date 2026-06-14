from __future__ import annotations

import os

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY", "")
HEADER_NAME = "Authori" + "zation"
HEADERS = {HEADER_NAME: BALLDONTLIE_API_KEY} if BALLDONTLIE_API_KEY else {}

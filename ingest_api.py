# Step 2 — Tasks 1 & 2: Error Handling + API Ingestion
# fetch_with_retry handles transient network errors (Task 1).
# fetch_api_records calls it and shapes the response into flat dicts (Task 2).
import logging
import time

import requests

logger = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_with_retry(url: str, params: dict, max_retries: int = 3, timeout: int = 10) -> dict:
    """Fetch url with exponential backoff on transient errors.

    Retry on: ConnectionError, Timeout, 5xx status codes.
    Fail immediately on: 4xx status codes.
    Log each retry attempt with the error and delay.
    """
    # TODO: implement retry loop with exponential backoff
    raise NotImplementedError


def fetch_api_records() -> list[dict]:
    """Fetch hourly weather from Open-Meteo and return flat dicts.

    Returns a list of dicts with keys: station, timestamp, temperature_c, humidity_pct.
    Returns [] if the API returns no data (do not raise an exception).
    """
    params = {
        "latitude": 55.67,
        "longitude": 12.56,
        "hourly": "temperature_2m,relative_humidity_2m",
        "forecast_days": 7,
    }
    # TODO:
    # - Call fetch_with_retry with API_URL and params
    # - The API returns {"hourly": {"time": [...], "temperature_2m": [...], "relative_humidity_2m": [...]}}
    # - Flatten to a list of dicts; set station="Open-Meteo Copenhagen" for all records
    raise NotImplementedError

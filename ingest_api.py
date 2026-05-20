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
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except(requests.exceptions.HTTPError) as e:
                if response.status_code < 500:
                    logger.error(f"HTTP error {response.status_code} Cannot retry!")
                    raise e
                if response.status_code >= 500:
                    logger.warning(f"Transient HTTP error {response.status_code} Retrying...")
                    if attempt == max_retries - 1:
                        raise e
                    wait_time = 2 ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed with error: {response.status}")
                    time.sleep(wait_time)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning(f"Transient network error: {e}. Retrying...")
            if attempt == max_retries - 1:
                raise e
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed with error: {e} Retrying in {wait_time} seconds...")
            time.sleep(wait_time)


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

    try:
        data = fetch_with_retry(API_URL,params)
        hourly = data.get("hourly",{})
        records = []
        for i, timestamp in enumerate(hourly.get("time",[])):
            records.append({
                "timestamp": timestamp,
                "temperature_c": hourly.get("temperature_2m",[])[i],
                "humidity_pct": hourly.get("relative_humidity_2m",[])[i],
                "station": "Open-Meteo Copenhagen",
                })

        logger.info(f"Fetched {len(records)} weather records")
        return records
    except Exception:
        return []


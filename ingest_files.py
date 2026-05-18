# Step 3 — Task 3: File Reading
# Read the messy CSV and normalize each row into the same dict format
# that fetch_api_records() produces, so validate_records() can handle both sources.
import csv
from pathlib import Path


def read_csv_records(path: Path) -> list[dict]:
    """Read weather_stations.csv and return normalized records.

    Returns a list of dicts with keys: station, timestamp, temperature_c, humidity_pct.

    Rules:
    - Open with newline="" and encoding="utf-8".
    - Use csv.DictReader.
    - Convert temperature_c to float and humidity_pct to int where possible.
    - Leave unconvertible values (e.g. "N/A", "") as-is so validation can catch them.
    """
    # TODO: implement CSV reading and normalization
    raise NotImplementedError

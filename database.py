# Step 5 — Task 5: Database Storage
# create_tables()  — run once at startup to set up raw_weather and weather_readings.
# insert_raw()     — store every record before validation so nothing is lost.
# upsert_readings()— insert valid records; ON CONFLICT updates instead of duplicating.
# count_readings() — query the final row count for the pipeline summary.
import sqlite3
from pathlib import Path

from models import WeatherReading

DB_PATH = Path("weather.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create raw_weather and weather_readings tables if they do not exist.

    raw_weather columns: id, station, timestamp, temperature_c, humidity_pct, source, ingested_at
    weather_readings columns: id, station, timestamp, temperature_c, humidity_pct
        + UNIQUE(station, timestamp) constraint for upserts
    """
    # TODO: use conn.execute() with CREATE TABLE IF NOT EXISTS statements
    raise NotImplementedError


def insert_raw(conn: sqlite3.Connection, records: list[dict], source: str) -> None:
    """Insert raw records (before validation) into raw_weather.

    Use parameterized queries with placeholder syntax; do not build SQL via string formatting.
    """
    # TODO: implement
    raise NotImplementedError


def upsert_readings(conn: sqlite3.Connection, readings: list[WeatherReading]) -> None:
    """Upsert valid WeatherReading objects into weather_readings.

    Use the upsert pattern to handle duplicate (station, timestamp) pairs.
    Use parameterized queries.
    """
    # TODO: implement
    raise NotImplementedError


def count_readings(conn: sqlite3.Connection) -> int:
    """Return the total number of rows in weather_readings."""
    # TODO: implement
    raise NotImplementedError

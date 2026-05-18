# Step 6 — Task 6: Pipeline Orchestration
# This is the entry point. It calls every module you built in steps 1–5 in order.
# Implement run_pipeline() so that `python3 -m pipeline` produces a summary and
# writes output/error_report.json. The auto-grader runs this file directly.
import json
import logging
from pathlib import Path

from database import count_readings, create_tables, get_connection, insert_raw, upsert_readings
from ingest_api import fetch_api_records
from ingest_files import read_csv_records
from validate import validate_records

OUTPUT_DIR = Path("output")
CSV_PATH = Path("data/weather_stations.csv")


def run_pipeline() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # TODO — implement each step in order:
    #
    # 1. Fetch records from Open-Meteo API using fetch_api_records()
    # 2. Read records from CSV using read_csv_records(CSV_PATH)
    # 3. Open a DB connection, create tables, insert all raw records (both sources)
    # 4. Validate all records — collect valid WeatherReading objects and error dicts
    # 5. Upsert valid records into weather_readings
    # 6. Save error dicts as JSON to output/error_report.json
    # 7. Print the pipeline summary in the format below.
    #
    # Note: the API count varies by time of day (Open-Meteo returns up to 168 hourly
    # records for 7 forecast days; the exact number depends on the current UTC hour).
    # The CSV contributes 6 invalid records and 4 valid ones; the duplicate Copenhagen
    # row is valid and exercises the upsert path rather than the validation error path.
    # Your actual output will look similar to this example:
    #
    #    === Pipeline Summary ===
    #    API records fetched: 166
    #    CSV records read: 10
    #    Total raw records: 176
    #    Valid records: 170
    #    Invalid records: 6
    #    Records in database: 169
    #    Error report: output/error_report.json

    raise NotImplementedError


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()

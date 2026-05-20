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
    api_fetching = fetch_api_records()
    csv_reading = read_csv_records(CSV_PATH)
    db_conn = get_connection()
    create_tables(db_conn)
    insert_raw(db_conn, api_fetching, source="API")
    insert_raw(db_conn, csv_reading, source="CSV")
    db_conn.commit()
    api_valid, api_errors = validate_records(api_fetching, source="API")
    csv_valid, csv_errors = validate_records(csv_reading, source="CSV")
    all_valid_readings = api_valid + csv_valid
    all_errors = api_errors + csv_errors
    upsert_readings(db_conn, all_valid_readings)
    db_conn.commit()
    with open(OUTPUT_DIR / "error_report.json", "w") as f:
        json.dump(all_errors, f, indent=2)
    total_in_db = count_readings(db_conn)
    print("=== Pipeline Summary ===")
    print(f"API records fetched: {len(api_fetching)}")
    print(f"CSV records read: {len(csv_reading)}")
    print(f"Total raw records: {len(api_fetching) + len(csv_reading)}")
    print(f"Valid records: {len(all_valid_readings)}")
    print(f"Invalid records: {len(all_errors)}")
    print(f"Records in database: {total_in_db}")
    print(f"Error report: {OUTPUT_DIR / 'error_report.json'}")
    db_conn.close()
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()

# AI Debugging Report

While building your pipeline you will run into at least one bug.
Document the debugging session below. If everything worked first try, introduce a bug intentionally and debug it.

---

## The Error

<!-- Paste the full Python traceback here. Include the error type, message, and the lines that caused it. 
$ python ingest_files.py
C:\Users\Beheerder\c55-data-week-3\ingest_files.py:47: SyntaxWarning: invalid escape sequence '\w'
  csv_path = Path("data\weather_stations.csv")
--- STARTING CSV PIPELINE TEST ---
I need to Know the coulmn name of the data: ['station', 'timestamp', 'temperature_c', 'humidity_pct']

--- TEST RESULTS ---
Total rows processed from CSV: 10

First 3 sample rows look like this:
{'station': 'Copenhagen', 'timestamp': '2025-01-15T10:00', 'temperature_c': 18.5, 'humidity_pct': None}
{'station': '', 'timestamp': '2025-01-15T11:00', 'temperature_c': 20.1, 'humidity_pct': None}
{'station': 'Aarhus', 'timestamp': '2025-01-15T12:00', 'temperature_c': 'N/A', 'humidity_pct': None}

Last row (to check for messy data parsing):
{'station': 'Kolding', 'timestamp': '2025-01-15T18:00', 'temperature_c': 14.9, 'humidity_pct': None} -->


## The Prompt

<!-- Paste the exact message you sent to the LLM (ChatGPT, Claude, etc.).
     Include: the error, the relevant code snippet, and what you asked the AI to help with. 
     $ python ingest_files.py
C:\Users\Beheerder\c55-data-week-3\ingest_files.py:47: SyntaxWarning: invalid escape sequence '\w'
  csv_path = Path("data\weather_stations.csv")
--- STARTING CSV PIPELINE TEST ---
I need to Know the coulmn name of the data: ['station', 'timestamp', 'temperature_c', 'humidity_pct']

--- TEST RESULTS ---
Total rows processed from CSV: 10

First 3 sample rows look like this:
{'station': 'Copenhagen', 'timestamp': '2025-01-15T10:00', 'temperature_c': 18.5, 'humidity_pct': None}
{'station': '', 'timestamp': '2025-01-15T11:00', 'temperature_c': 20.1, 'humidity_pct': None}
{'station': 'Aarhus', 'timestamp': '2025-01-15T12:00', 'temperature_c': 'N/A', 'humidity_pct': None}

Last row (to check for messy data parsing):
{'station': 'Kolding', 'timestamp': '2025-01-15T18:00', 'temperature_c': 14.9, 'humidity_pct': None}
i just wanted to understand this file but way i got None for temp and humidity?
     -->

## The Solution

<!-- What did the AI suggest?
     Did you apply the suggestion as-is, or did you need to adapt it? Explain what changed. 
     The output you are seeing shows that your file reading logic is working, but it highlights exactly why data pipelines need a validation step! You are getting `None` and strings like `'N/A'` because the raw CSV file contains messy, missing, or corrupted data.

Let's break down exactly why `temperature_c` and `humidity_pct` look like that in your sample rows:

---

## 1. Why `humidity_pct` is always `None`

In your first three sample rows and your last row, **every single `humidity_pct` value is `None`.** There are two likely reasons for this:

* **The CSV column is completely empty:** The actual `weather_stations.csv` file might have headers for humidity, but the rows below it are blank or missing data entirely for that column.
* **A column name mismatch:** Look closely at your print statement:
```text
I need to Know the coulmn name of the data: ['station', 'timestamp', 'temperature_c', 'humidity_pct']

```


If the CSV file spells it slightly differently (for example, `humidity` or `humidity_%`), your Python CSV reader won't find an exact match for `"humidity_pct"`, so it defaults to filling that key with `None`.

---

## 2. Why `temperature_c` has `'N/A'` and missing values

Look at your third sample row:

```python
{'station': 'Aarhus', 'timestamp': '2025-01-15T12:00', 'temperature_c': 'N/A', 'humidity_pct': None}

```

The temperature here is the **text string `'N/A'**` instead of a number like `18.5`. This happens because whoever recorded the data at the Aarhus station didn't provide a reading, and typed "N/A" into the file.

---

## This is exactly why Task 4 (Pydantic Validation) exists!

This test print perfectly proves why your pipeline cannot just blindly push raw CSV data straight into the clean `weather_readings` database table:

1. **Database Crash Prevention:** Your database table requires `temperature_c` to be a `REAL` (decimal) number and `humidity_pct` to be an `INTEGER`. If you tried to save the text string `'N/A'` or the value `None` into a column that expects numbers, SQLite would throw an error or save broken data.
2. **How Pydantic saves the day:** When these rows hit your `validate_records()` function, Pydantic will flag them:
* The row with `station: ''` (empty string) will fail because station is marked as `NOT NULL` or requires a minimum length.
* The Aarhus row will fail because `'N/A'` cannot be converted into a float number.
* These broken rows will be safely filtered out and sent to your `error_report.json`, leaving only the 100% clean, valid rows to enter your final database!
 -->

## Reflection

<!-- Did you understand *why* the code was broken before you got the AI's answer?
     After the fix: do you understand why it works now?
     What would you do differently next time you hit this type of error?
     
     I was not sure if the None values are related to the spelling mistakes or something else but after the ai's answer i noticed where is the problem was exactly in my code
      -->

#!/usr/bin/env bash
# Auto-grade Week 3 assignment. Writes score.json next to this script.
# Total = 100, passing = 60.
#
# Run from repo root: bash .hyf/test.sh
# Or from .hyf/: bash test.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PASSING=60

# Initialise score.json to 0 immediately so a crash before the final write
# does not leave a stale result from a previous run.
cat > "$SCRIPT_DIR/score.json" <<'INIT'
{"score": 0, "pass": false, "passingScore": 60}
INIT

# Remove runtime-generated files so each grader run starts from a clean state.
# In CI the checkout is always clean; locally this prevents stale artifacts from
# a previous successful run inflating the score on a broken re-submission.
rm -f weather.db output/error_report.json

# --- Tasks 1-6: Ingestion Pipeline (70 points) ---
#
# Scoring ladder (each level requires all previous levels to pass):
#   0   nothing committed
#   10  required files all present
#   20  pipeline runs without crashing
#   40  output/error_report.json is valid + weather.db has rows
#   50  pipeline is idempotent (same row count on second run)
#   70  code uses required patterns (@field_validator, parameterized queries,
#       ON CONFLICT upsert, time.sleep backoff)
task16=0
task16_msg="missing required files"

required_files=(
    "models.py"
    "ingest_api.py"
    "ingest_files.py"
    "validate.py"
    "database.py"
    "pipeline.py"
    ".env.example"
)

all_present=true
for f in "${required_files[@]}"; do
    if [ ! -f "$f" ]; then
        all_present=false
        break
    fi
done

if [ "$all_present" = true ]; then
    task16=10
    task16_msg="files exist but pipeline failed to run"

    if [ -f requirements.txt ]; then
        python3 -m pip install -q -r requirements.txt || \
            echo "WARN: pip install failed; pipeline may crash with ModuleNotFoundError" >&2
    fi

    PIPELINE_ERR=$(mktemp)
    if python3 -m pipeline >/dev/null 2>"$PIPELINE_ERR"; then
        task16=20
        task16_msg="pipeline ran but output checks failed"

        STRUCT_ERR=$(mktemp)
        if python3 - <<'PY' 2>"$STRUCT_ERR"
import json, sqlite3
from pathlib import Path

# error_report.json must exist and be a non-empty list of error objects
rpt = Path("output/error_report.json")
assert rpt.exists(), "output/error_report.json was not created"
errors = json.loads(rpt.read_text())
assert isinstance(errors, list), "error_report.json must be a JSON list"
assert len(errors) > 0, "error_report.json is empty — the CSV has intentional bad rows that should fail validation"

required_fields = {"index", "source", "raw_record", "error_details"}
for i, e in enumerate(errors[:3]):
    missing = required_fields - set(e.keys())
    assert not missing, f"error object {i} missing fields: {missing}"

# weather.db must exist and have rows
db = Path("weather.db")
assert db.exists(), "weather.db was not created"
conn = sqlite3.connect(db)
count = conn.execute("SELECT COUNT(*) FROM weather_readings").fetchone()[0]
assert count > 0, "weather_readings table is empty after pipeline run"
PY
        then
            rm -f "$STRUCT_ERR"
            task16=40
            task16_msg="output checks passed; testing idempotency"

            # Idempotency: run a second time, row count must stay the same
            count_before=$(python3 -c "
import sqlite3
conn = sqlite3.connect('weather.db')
print(conn.execute('SELECT COUNT(*) FROM weather_readings').fetchone()[0])
")
            if python3 -m pipeline >/dev/null 2>&1; then
                count_after=$(python3 -c "
import sqlite3
conn = sqlite3.connect('weather.db')
print(conn.execute('SELECT COUNT(*) FROM weather_readings').fetchone()[0])
")
                if [ "$count_before" = "$count_after" ]; then
                    task16=50
                    task16_msg="output + idempotency pass; checking code patterns"

                    # Code introspection for the final 20 points.
                    # Patterns target actual code constructs, not docstrings:
                    #   execute.*?    — SQL placeholder in an execute() call
                    #   ON CONFLICT   — upsert keyword in actual SQL string
                    #   time\.sleep   — stdlib sleep call (avoids the function
                    #                   name "fetch_with_retry" or docstring words)
                    has_field_validator=$(grep -cE "@field_validator" models.py || true)
                    has_classmethod=$(grep -cE "@classmethod" models.py || true)
                    # Parameterized queries: check for ? placeholder anywhere in the file
                    # AND an execute call — handles both inline and multi-line SQL forms.
                    has_q=$(grep -c "?" database.py || true)
                    has_exec=$(grep -cE "\.execute" database.py || true)
                    if [ "$has_q" -gt 0 ] && [ "$has_exec" -gt 0 ]; then has_param_queries=1; else has_param_queries=0; fi
                    has_on_conflict=$(grep -ciE "ON CONFLICT" database.py || true)
                    has_sleep=$(grep -cE "time\.sleep" ingest_api.py || true)

                    if [ "$has_field_validator" -gt 0 ] && \
                       [ "$has_classmethod" -gt 0 ] && \
                       [ "$has_param_queries" -gt 0 ] && \
                       [ "$has_on_conflict" -gt 0 ] && \
                       [ "$has_sleep" -gt 0 ]; then
                        task16=70
                        task16_msg="pipeline + idempotency + code patterns all pass"
                    else
                        missing_patterns=()
                        [ "$has_field_validator" -eq 0 ] && missing_patterns+=("@field_validator in models.py")
                        [ "$has_classmethod" -eq 0 ] && missing_patterns+=("@classmethod in models.py")
                        [ "$has_param_queries" -eq 0 ] && missing_patterns+=("parameterized ? in execute() in database.py")
                        [ "$has_on_conflict" -eq 0 ] && missing_patterns+=("ON CONFLICT in database.py")
                        [ "$has_sleep" -eq 0 ] && missing_patterns+=("time.sleep backoff in ingest_api.py")
                        task16_msg="output passes but code missing: $(IFS=, ; echo "${missing_patterns[*]}")"
                    fi
                else
                    task16_msg="second run changed row count ($count_before -> $count_after); upsert not working"
                fi
            fi
        else
            err=$(tail -3 "$STRUCT_ERR" | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ //;s/ $//')
            [ -n "$err" ] && task16_msg="output check failed: $err"
            rm -f "$STRUCT_ERR"
        fi
    else
        err=$(tail -3 "$PIPELINE_ERR" | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ //;s/ $//')
        [ -n "$err" ] && task16_msg="pipeline failed to run: $err"
    fi
    rm -f "$PIPELINE_ERR"
fi

# --- Task 7: Azure CLI + Portal (15 points) ---
#
#  5 pts  output/azure_resource_groups.json exists and is valid JSON
# 10 pts  output/azure_compare.md exists
# 15 pts  output/azure_compare.md has all 3 sections and is filled in (>1200 chars,
#         which is above the committed template's ~233 bytes)
task7=0
task7_msg="missing output/azure_resource_groups.json"

if [ -s "output/azure_resource_groups.json" ]; then
    if python3 -c "import json; json.load(open('output/azure_resource_groups.json'))" 2>/dev/null; then
        task7=5
        task7_msg="azure_resource_groups.json is valid JSON; azure_compare.md missing or not filled in"

        if [ -s "output/azure_compare.md" ]; then
            task7=10
            task7_msg="azure_compare.md exists but looks too short or missing sections"
            section_count=$(grep -cE "^## " output/azure_compare.md || true)
            char_count=$(wc -c < output/azure_compare.md)
            if [ "$section_count" -ge 3 ] && [ "$char_count" -gt 1200 ]; then
                task7=15
                task7_msg="azure_resource_groups.json and azure_compare.md both present and filled in"
            fi
        fi
    else
        task7_msg="output/azure_resource_groups.json is not valid JSON"
    fi
fi

# --- Task 8: AI Debug Report (15 points) ---
#
#  5 pts  AI_DEBUG.md exists
# 10 pts  all four sections present (## The Error, ## The Prompt, ## The Solution, ## Reflection)
# 15 pts  file is meaningfully filled in (>1800 chars)
task8=0
task8_msg="missing AI_DEBUG.md"

if [ -s "AI_DEBUG.md" ]; then
    task8=5
    task8_msg="AI_DEBUG.md exists but missing required sections"
    if grep -q "^## The Error" AI_DEBUG.md && \
       grep -q "^## The Prompt" AI_DEBUG.md && \
       grep -q "^## The Solution" AI_DEBUG.md && \
       grep -q "^## Reflection" AI_DEBUG.md; then
        task8=10
        task8_msg="all sections present but file looks too short to be filled in"
        if [ "$(wc -c < AI_DEBUG.md)" -gt 1800 ]; then
            task8=15
            task8_msg="AI_DEBUG.md is filled in"
        fi
    fi
fi

score=$((task16 + task7 + task8))
if [ "$score" -ge "$PASSING" ]; then pass=true; else pass=false; fi

cat > "$SCRIPT_DIR/score.json" <<EOF
{
  "score": $score,
  "pass": $pass,
  "passingScore": $PASSING
}
EOF

echo "Tasks 1-6 (Ingestion Pipeline): $task16/70 — $task16_msg"
echo "Task 7  (Azure CLI + Portal):   $task7/15  — $task7_msg"
echo "Task 8  (AI Debug Report):      $task8/15  — $task8_msg"
echo "----------------------------------------"
echo "Total: $score/100 — pass=$pass (passing threshold: $PASSING)"

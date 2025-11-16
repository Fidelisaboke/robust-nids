#!/usr/bin/env bash
# Scripts/get_json_sample.sh
# Usage: ./scripts/get_json_sample.sh data/flows/test_results/infogathering.csv

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_csv>"
    exit 1
fi

CSV_FILE="$1"

# 1. Get the header row
HEADER=$(head -n 1 "$CSV_FILE")

# 2. Get ONE random data row (shuf), ensuring we don't pick the header again
# tail -n +2 starts from line 2, skipping header.
DATA_ROW=$(tail -n +2 "$CSV_FILE" | shuf -n 1)

# 3. Combine them and pipe to Python for perfect JSON formatting
# We use csv.DictReader so it handles weird quoting/spacing automatically.
echo -e "$HEADER\n$DATA_ROW" | python3 -c "
import csv, json, sys
reader = csv.DictReader(sys.stdin)
for row in reader:
    # Convert numeric-looking strings to actual numbers for nicer JSON
    for k, v in row.items():
        try:
            row[k] = float(v) if '.' in v else int(v)
        except (ValueError, TypeError):
            pass # Keep as string if not a number
    print(json.dumps(row, indent=2))
"

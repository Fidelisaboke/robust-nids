#!/usr/bin/env bash
#
# Prunes old alerts from the database.
#
# Usage:
# ./backend/scripts/prune_alerts.sh
#   (Prunes alerts > 30 days old)
#
# ./backend/scripts/prune_alerts.sh 90
#   (Prunes alerts > 90 days old)
#
# ./backend/scripts/prune_alerts.sh 30 --dry-run
#   (Show how many alerts would be pruned)
#

set -e

# --- Environment Setup ---
# Get the absolute path to the root of the project
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_PYTHON="$REPO_ROOT/backend/.venv/bin/python3"
PYTHON_SCRIPT="$REPO_ROOT/backend/utils/prune_alerts.py"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python venv not found at $VENV_PYTHON"
    exit 1
fi
# ------------------------

# Get arguments passed to this script (e.g., "90", "--dry-run")
# If no day is provided, default to 30.
DAYS=${1:-30}
EXTRA_ARGS=${*:2}

echo "========================================="
echo "🧹 Pruning NIDS Alerts"
echo "========================================="
echo "   Keeping last: $DAYS days"
if [ "$EXTRA_ARGS" = "--dry-run" ]; then
    echo "   Mode: DRY RUN (no data will be deleted)"
fi
echo "========================================="

# Run the Python script with all provided arguments
"$VENV_PYTHON" "$PYTHON_SCRIPT" --days "$DAYS" $EXTRA_ARGS

echo "========================================="
echo "✅ Pruning complete."
echo "========================================="

### 3. How to Automate It (Cron Job)

# To make this run "periodically" (e.g., every night at 3:00 AM), you can add it to your server's crontab.

# 1.  Run crontab -e on your server.
# 2.  Add this line to the bottom:
#
#     # Prune old NIDS alerts every night at 3:00 AM
#     0 3 * * * /bin/bash /path/to/your/project/backend/scripts/prune_alerts.sh 90

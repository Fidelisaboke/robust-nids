#!/usr/bin/env bash
# scripts/reset_alerts.sh
# Clears the live alert feed on the running backend.

set -e

API_URL="http://127.0.0.1:8000/api/v1/nids/live-events"

echo "========================================"
echo "🗑️  Clearing NIDS Live Alerts..."
echo "========================================"

# Use curl to send a DELETE request
if curl -s -X DELETE "$API_URL" >/dev/null; then
    echo "✅ Alerts cleared successfully."
else
    echo "❌ Failed to clear alerts. Is the backend running?"
    exit 1
fi

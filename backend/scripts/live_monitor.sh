#!/usr/bin/env bash
# scripts/live_monitor.sh
# Continuous traffic capture with 10-second rotation.

set -e

# Directory for live pcap chunks
CAPTURE_DIR="/tmp/nids_live"
sudo mkdir -p "$CAPTURE_DIR"
sudo chmod 777 "$CAPTURE_DIR"

echo "========================================"
echo "  NIDS Live Capture Agent Started"
echo "========================================"
echo "Saving 10s chunks to: $CAPTURE_DIR"
echo "Press Ctrl+C to stop."

# -i any: Capture all interfaces (localhost + internet)
# -G 10: Rotate every 10 seconds
# -n: Don't resolve DNS (faster)
# -Z root: Stay as root to avoid 'Permission denied' when writing files
sudo tcpdump -i any -G 10 -n -Z root -w "$CAPTURE_DIR/capture_%Y%m%d%H%M%S.pcap"

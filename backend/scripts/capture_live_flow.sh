#!/usr/bin/env bash
# capture_live_flow.sh
# Captures *all* traffic on a live interface for a duration.
# Usage: sudo ./scripts/capture_live_flow.sh [duration_seconds] [interface]

set -eu

# --- 1. Sudo Check & Basic Setup ---
if [ "$EUID" -ne 0 ]; then
  echo "ERROR: Please run this script with sudo."
  echo "Usage: sudo $0 [duration_seconds] [interface]"
  exit 1
fi

DURATION=${1:-60}
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST_DIR="$REPO_ROOT/data/flows/test_results"
ORIGINAL_USER=${SUDO_USER:-$(whoami)}
ORIGINAL_GROUP=$(id -gn "$ORIGINAL_USER")

# --- Auto-detect interface if not provided ---
if [ -n "${2:-}" ]; then
  CAP_IF="$2"
else
  # Try to auto-detect the default interface
  CAP_IF=$(ip route | grep default | awk '{print $5}' | head -n1)
  if [ -z "$CAP_IF" ]; then
    echo "ERROR: Could not auto-detect network interface."
    echo "Please specify manually: sudo $0 $DURATION <interface>"
    echo ""
    echo "Available interfaces:"
    ip -br link show | grep -v "lo" | awk '{print "  - " $1}'
    exit 1
  fi
fi

# Verify interface exists
if ! ip link show "$CAP_IF" >/dev/null 2>&1; then
  echo "ERROR: Interface '$CAP_IF' does not exist."
  echo ""
  echo "Available interfaces:"
  ip -br link show | grep -v "lo" | awk '{print "  - " $1}'
  exit 1
fi

TS=$(date +%Y%m%d_%H%M%S)
TMP_PCAP="/tmp/live_flow_${TS}.pcap"

# --- 2. Check for Tools ---
if ! command -v tcpdump >/dev/null 2>&1; then
  echo "ERROR: tcpdump is required. (sudo apt install tcpdump)"
  exit 1
fi

echo "========================================="
echo "Live Traffic Capture"
echo "========================================="
echo "Interface: $CAP_IF"
echo "Duration: ${DURATION}s"
echo "Output: $DEST_DIR/live_flow_${TS}.pcap"
echo "Owner: $ORIGINAL_USER:$ORIGINAL_GROUP"
echo ""
echo "INSTRUCTIONS:"
echo "  1. This script will capture ALL traffic on $CAP_IF"
echo "  2. To generate benign traffic, open another terminal and:"
echo "     - Browse websites: curl https://www.google.com"
echo "     - Stream video: youtube-dl or watch YouTube"
echo "     - Download files: wget https://example.com/largefile.zip"
echo "  3. Traffic will be captured for ${DURATION} seconds"
echo "========================================="
echo ""
read -p "Press ENTER to start capture..."

mkdir -p "$DEST_DIR"

# --- 3. Start Capture ---
echo "Starting capture on $CAP_IF..."
CAP_PID=""
tcpdump -i "$CAP_IF" -s 0 -w "$TMP_PCAP" 2>/dev/null &
CAP_PID=$!

# Progress indicator
for i in $(seq 1 "$DURATION"); do
  sleep 1
  printf "\rCapturing... %02d/%02d seconds" "$i" "$DURATION"
done
echo ""

echo "Stopping tcpdump..."
kill -INT "$CAP_PID" 2>/dev/null || kill -TERM "$CAP_PID" 2>/dev/null || true
wait "$CAP_PID" 2>/dev/null || true
sleep 1

# --- 4. Verify and Clean Up ---
if [ ! -s "$TMP_PCAP" ]; then
  echo "WARNING: PCAP file was created but is EMPTY."
  echo "Possible reasons:"
  echo "  1. Wrong interface (you specified: $CAP_IF)"
  echo "  2. No traffic was generated during capture"
  echo "  3. Insufficient permissions"
  rm -f "$TMP_PCAP"
  exit 1
fi

# Show basic stats
PACKET_COUNT=$(tcpdump -r "$TMP_PCAP" 2>/dev/null | wc -l)
FILE_SIZE=$(du -h "$TMP_PCAP" | cut -f1)

chown "$ORIGINAL_USER":"$ORIGINAL_GROUP" "$TMP_PCAP"
mv "$TMP_PCAP" "$DEST_DIR/"

echo ""
echo "========================================="
echo "Capture Complete!"
echo "========================================="
echo "File: $DEST_DIR/live_flow_${TS}.pcap"
echo "Size: $FILE_SIZE"
echo "Packets: $PACKET_COUNT"
echo ""
echo "Next steps:"
echo "  1. Convert to CSV: ./scripts/process_pcaps.sh"
echo "  2. Run inference on the CSV"
echo "========================================="

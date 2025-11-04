#!/usr/bin/env bash
# capture_sample_flow.sh
# Usage: sudo ./scripts/traffic_capture/capture_sample_flow.sh [duration_seconds]

set -eu

# --- 1. Sudo Check ---
if [ "$EUID" -ne 0 ]; then
  echo "ERROR: Please run this script with sudo."
  echo "Usage: sudo $0 [duration_seconds]"
  exit 1
fi

DURATION=${1:-20}
TS=$(date +%Y%m%d_%H%M%S)
TMP_PCAP="/tmp/flow_${TS}.pcap"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST_DIR="$REPO_ROOT/data/flows/pcap"

ORIGINAL_USER=${SUDO_USER:-$(whoami)}
ORIGINAL_GROUP=$(id -gn "$ORIGINAL_USER")
CAP_IF="lo" # Capture on loopback

# Helper function
_safe_kill() {
  local pid=$1
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
}

# --- 2. Check for Capture Tools ---
CAP_CMD=""
if command -v tcpdump >/dev/null 2>&1; then
  CAP_CMD="tcpdump"
elif command -v tshark >/dev/null 2>&1; then
  CAP_CMD="tshark"
else
  echo "ERROR: Neither tcpdump nor tshark found. Install one (e.g. sudo apt install tcpdump tshark)."
  exit 1
fi

echo "Capture tool: $CAP_CMD"
echo "Capture interface: $CAP_IF"
echo "Duration: ${DURATION}s"
echo "PCAP will be owned by: $ORIGINAL_USER:$ORIGINAL_GROUP"

mkdir -p "$DEST_DIR"

# --- 3. Robust Traffic Generation ---
PIDS=()

# Create test file FIRST
echo "Creating /tmp/testfile.bin..."
rm -f /tmp/testfile.bin
dd if=/dev/urandom of=/tmp/testfile.bin bs=1M count=1 status=none || {
    echo "ERROR: Failed to create /tmp/testfile.bin even as root."
    exit 1
}

# 1) Start HTTP server
echo "Starting Python HTTP server in /tmp..."
cd /tmp
python3 -m http.server 8000 >/dev/null 2>&1 &
PIDS+=("$!")
cd "$REPO_ROOT" # Go back to original dir

# 2) iperf3
if command -v iperf3 >/dev/null 2>&1; then
  echo "Starting iperf3 server+client..."
  iperf3 -s >/dev/null 2>&1 &
  PIDS+=("$!")
  sleep 0.5
  iperf3 -c 127.0.0.1 -t "$DURATION" -P 3 >/dev/null 2>&1 &
  PIDS+=("$!")
else
  echo "WARNING: iperf3 not found. Traffic will be minimal."
  echo "Install it with: sudo apt install iperf3"
fi

# 3) Ping
ping -c 5 127.0.0.1 >/dev/null 2>&1 & PIDS+=("$!")

# 4) curl loop
echo "Starting curl loop..."
( sleep 1
  for i in $(seq 1 5); do
    curl -s -o /dev/null http://127.0.0.1:8000/testfile.bin || true
    sleep 1
  done ) &
PIDS+=("$!")

# --- 4. Start Capture (with error reporting) ---
CAP_PID=""
echo "Starting capture on interface '$CAP_IF'..."
if [ "$CAP_CMD" = "tcpdump" ]; then
  # Removed >/dev/null 2>&1 to see errors
  tcpdump -i "$CAP_IF" -s 0 -w "$TMP_PCAP" &
  CAP_PID=$!
elif [ "$CAP_CMD" = "tshark" ]; then
  # Removed >/dev/null 2>&1 to see errors
  tshark -i "$CAP_IF" -a duration:"$DURATION" -w "$TMP_PCAP" &
  CAP_PID=$!
fi

echo "Waiting ${DURATION}s for capture to complete..."
sleep "$DURATION"

# Stop tcpdump
if [ "$CAP_CMD" = "tcpdump" ] && [ -n "$CAP_PID" ]; then
  echo "Stopping tcpdump (pid $CAP_PID)..."
  kill -INT "$CAP_PID" 2>/dev/null || kill -TERM "$CAP_PID" 2>/dev/null || true
  wait "$CAP_PID" 2>/dev/null || true
fi

sleep 1

# --- 5. Verify and Clean Up ---
if [ ! -s "$TMP_PCAP" ]; then # -s checks if file exists and is not empty
  echo "------------------------------------------------------"
  echo "ERROR: PCAP file was not created or is EMPTY."
  echo "This means '$CAP_CMD' failed to capture on '$CAP_IF'."
  echo "Check for error messages above."
  echo "------------------------------------------------------"
  exit 1
fi

# Change owner and move
chown "$ORIGINAL_USER":"$ORIGINAL_GROUP" "$TMP_PCAP"
mv "$TMP_PCAP" "$DEST_DIR/"

# Clean up
echo "Cleaning up background processes..."
for pid in "${PIDS[@]:-}"; do
  _safe_kill "$pid" || true
done
rm -f /tmp/testfile.bin

echo ""
echo "Capture saved to: $DEST_DIR/$(basename "$TMP_PCAP")"
echo "Done."

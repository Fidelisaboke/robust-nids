#!/usr/bin/env bash
# capture_malicious_flow.sh
# Generates and captures malicious-pattern traffic (nmap port scan) on 'lo'.
# Usage: sudo ./scripts/traffic_capture/capture_malicious_flow.sh [duration_seconds]

set -eu

# --- 1. Sudo Check & Basic Setup ---
if [ "$EUID" -ne 0 ]; then
  echo "ERROR: Please run this script with sudo."
  echo "Usage: sudo $0 [duration_seconds]"
  exit 1
fi

DURATION=${1:-10} # 10s is plenty for a port scan
TS=$(date +%Y%m%d_%H%M%S)
TMP_PCAP="/tmp/malicious_flow_${TS}.pcap"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST_DIR="$REPO_ROOT/data/flows/pcap"

ORIGINAL_USER=${SUDO_USER:-$(whoami)}
ORIGINAL_GROUP=$(id -gn "$ORIGINAL_USER")
CAP_IF="lo"

# Helper function
_safe_kill() {
  local pid=$1
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
}

# --- 2. Check for Tools ---
if ! command -v tcpdump >/dev/null 2>&1; then
  echo "ERROR: tcpdump is required. (sudo apt install tcpdump)"
  exit 1
fi
if ! command -v nmap >/dev/null 2>&1; then
  echo "ERROR: nmap is required for this script. (sudo apt install nmap)"
  exit 1
fi

echo "Capture tool: tcpdump"
echo "Capture interface: $CAP_IF"
echo "Duration: ${DURATION}s"
echo "PCAP will be owned by: $ORIGINAL_USER:$ORIGINAL_GROUP"

mkdir -p "$DEST_DIR"

# --- 3. Malicious Traffic Generation ---
PIDS=()
echo "Starting 'malicious' traffic generators..."

# 1) Start a simple server for nmap to find
python3 -m http.server 8000 >/dev/null 2>&1 &
PIDS+=("$!")
python3 -m http.server 8001 >/dev/null 2>&1 &
PIDS+=("$!")
sleep 0.5 # Give servers time to start

# 2) Run nmap to generate "Information Gathering" traffic.
# -sS: A stealthy SYN scan (classic suspicious traffic)
# -T4: Speeds it up
# -p-: Scans all 65535 ports
echo "Starting nmap port scan (this will look malicious)..."
nmap -sS -T4 -p- 127.0.0.1 >/dev/null 2>&1 &
PIDS+=("$!")
sleep 1 # Give nmap time to start

# --- 4. Start Capture ---
CAP_PID=""
echo "Starting capture on interface '$CAP_IF'..."
tcpdump -i "$CAP_IF" -s 0 -w "$TMP_PCAP" &
CAP_PID=$!

echo "Waiting ${DURATION}s for capture to complete..."
sleep "$DURATION"

echo "Stopping tcpdump (pid $CAP_PID)..."
kill -INT "$CAP_PID" 2>/dev/null || kill -TERM "$CAP_PID" 2>/dev/null || true
wait "$CAP_PID" 2>/dev/null || true
sleep 1

# --- 5. Verify and Clean Up ---
if [ ! -s "$TMP_PCAP" ]; then
  echo "ERROR: PCAP file was not created or is EMPTY."
  exit 1
fi

chown "$ORIGINAL_USER":"$ORIGINAL_GROUP" "$TMP_PCAP"
mv "$TMP_PCAP" "$DEST_DIR/"

echo "Cleaning up background processes..."
for pid in "${PIDS[@]:-}"; do
  _safe_kill "$pid" || true
done

echo ""
echo "Malicious capture saved to: $DEST_DIR/$(basename "$TMP_PCAP")"
echo "Done."

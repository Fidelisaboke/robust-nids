#!/usr/bin/env bash
# scripts/run_dos.sh
#
# Targeted DoS Demo for NIDS.
# Runs a high-rate TCP ACK flood to trigger "DoS/Mirai" alerts.
#
# Usage: sudo ./scripts/run_dos.sh [TARGET_IP]

set -e

# --- Configuration ---
TARGET_IP=${1:-"127.0.0.1"}
TARGET_PORT=9999
DURATION_SECONDS=15

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Cleanup Trap ---
cleanup() {
    echo -e "\n${BLUE}[INFO] Cleaning up...${NC}"
    kill $NC_PID 2>/dev/null || true
}
trap cleanup EXIT

# --- Prerequisites ---
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run with sudo.${NC}"
    exit 1
fi
if ! command -v hping3 >/dev/null 2>&1; then
    echo -e "${RED}[ERROR] 'hping3' is missing. Install it: sudo apt install hping3${NC}"
    exit 1
fi

# --- Setup ---
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}       NIDS DEMO: DoS ATTACK (FLOOD)     ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. Start dummy listener (so packets have a destination)
echo -e "\n${GREEN}[1/2] Starting dummy listener on $TARGET_IP:$TARGET_PORT...${NC}"
# Use python for a robust listener if nc is flaky, but nc is usually fine for just accepting packets
if command -v nc >/dev/null 2>&1; then
    nc -l -k -p $TARGET_PORT >/dev/null 2>&1 &
    NC_PID=$!
else
    # Fallback to python if netcat is missing
    python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', $TARGET_PORT)); s.listen(5); [s.accept() for _ in iter(int,1)]" >/dev/null 2>&1 &
    NC_PID=$!
fi
sleep 2

echo ">> Dashboard Expectation: 'Critical' threat for 'DoS' or 'Mirai'."
read -p "Press ENTER to launch ${DURATION_SECONDS}s flood..."

# 2. Launch Attack
echo -e "\n${RED}[2/2] LAUNCHING TCP ACK FLOOD!${NC}"
# -A: ACK flood (typical of many botnets)
# -p: Target port
# -i u1000: Wait 1000 microseconds (1ms) between packets = ~1000 pkts/sec
# --rand-source: Spoof source IP (makes it look like a distributed attack)
timeout $DURATION_SECONDS hping3 -A -p $TARGET_PORT -i u1000 --rand-source "$TARGET_IP" || true

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}     ATTACK FINISHED${NC}"
echo -e "${BLUE}=========================================${NC}"

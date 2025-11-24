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
DURATION_SECONDS=10 # Attack runs for 10 seconds
PACKET_RATE_MICROSECONDS=500 # 500µs delay = 2000 packets/sec

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

# 1. Start dummy listener
echo -e "\n${GREEN}[1/2] Starting dummy listener on $TARGET_IP:$TARGET_PORT...${NC}"
if command -v nc >/dev/null 2>&1; then
    nc -l -k -p $TARGET_PORT >/dev/null 2>&1 &
    NC_PID=$!
else
    # Python fallback listener
    python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', $TARGET_PORT)); s.listen(5); [s.accept() for _ in iter(int,1)]" >/dev/null 2>&1 &
    NC_PID=$!
fi
sleep 2

echo ">> Generating DoS Traffic Flows."
read -p "Press ENTER to launch ${DURATION_SECONDS}s flood..."

# 2. Launch Attack
echo -e "\n${RED}[2/2] LAUNCHING TCP ACK FLOOD!${NC}"
# -i u500: 500µs delay = 2000 packets/sec (Aggressive signature)
# --rand-source: Essential for forcing one-way, stateless flow
# -c 20000: Total packets for 10 seconds at 2000pps
timeout $DURATION_SECONDS sudo hping3 -A -p $TARGET_PORT -i u${PACKET_RATE_MICROSECONDS} -c 20000 --rand-source "$TARGET_IP" >/dev/null 2>&1 || true

# Wait for file rotation to complete
echo -e "\n${BLUE}[INFO] Waiting 5s for capture chunk closure...${NC}"
sleep 5

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}     ATTACK FINISHED (Check Processor Log) ${NC}"
echo -e "${BLUE}=========================================${NC}"

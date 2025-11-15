#!/usr/bin/env bash
# scripts/demo_bruteforce.sh
#
# Targeted Bruteforce Demo for NIDS.
# Spins up a vulnerable service and attacks it to generate realistic alerts.
#
# Usage: sudo ./scripts/demo_bruteforce.sh [TARGET_IP]

set -e

# --- Configuration ---
TARGET_IP=${1:-"127.0.0.1"}
TARGET_PORT=8085
USER_LIST="/tmp/demo_users.txt"
PASS_LIST="/tmp/demo_pass.txt"
DURATION_SECONDS=30  # How long the attack should last

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Cleanup Trap ---
cleanup() {
    echo -e "\n${BLUE}[INFO] Cleaning up...${NC}"
    kill $HTTP_PID 2>/dev/null || true
    rm -f "$USER_LIST" "$PASS_LIST"
}
trap cleanup EXIT

# --- Prerequisites ---
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run with sudo.${NC}"
    exit 1
fi
if ! command -v hydra >/dev/null 2>&1; then
    echo -e "${RED}[ERROR] 'hydra' is missing. Install it: sudo apt install hydra${NC}"
    exit 1
fi

# --- Setup ---
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}     NIDS DEMO: BRUTEFORCE ATTACK     ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. Create dummy wordlists
echo -e "\n${GREEN}[1/3] Generating attack wordlists...${NC}"
echo -e "admin\nroot\nuser" > "$USER_LIST"
# Smaller list, we will just loop the attack to sustain it
for i in {1..50}; do echo "wrongpass$i" >> "$PASS_LIST"; done

# 2. Start vulnerable service
echo -e "${GREEN}[2/3] Starting vulnerable HTTP service on $TARGET_IP:$TARGET_PORT...${NC}"
python3 -m http.server $TARGET_PORT --bind $TARGET_IP >/dev/null 2>&1 &
HTTP_PID=$!
sleep 2

echo -e "${GREEN}Service is UP. Attack ready.${NC}"
echo ">> Dashboard Expectation: 'Critical' threat for 'Bruteforce'."
read -p "Press ENTER to launch 30s sustained attack..."

# 3. Launch Sustained Attack
echo -e "\n${RED}[3/3] LAUNCHING SUSTAINED ATTACK (${DURATION_SECONDS}s)...${NC}"
END_TIME=$((SECONDS + DURATION_SECONDS))

while [ $SECONDS -lt $END_TIME ]; do
    # -t 8: High parallelism for volume
    # -w 1: Wait 1s (Minimum allowed by newer Hydra versions)
    # We redirect output to keep the terminal clean during the loop
    hydra -L "$USER_LIST" -P "$PASS_LIST" -t 8 -w 1 "http-get://$TARGET_IP:$TARGET_PORT/" >/dev/null 2>&1 || true
    echo -n "." # Progress indicator
    sleep 0.5
done

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}     ATTACK FINISHED${NC}"
echo -e "${BLUE}=========================================${NC}"

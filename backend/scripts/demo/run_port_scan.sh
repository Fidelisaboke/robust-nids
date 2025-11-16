#!/usr/bin/env bash
# scripts/run_port_scan.sh
#
# Targeted Port Scan Demo for NIDS.
# Runs a noisy Nmap SYN scan to generate "Information Gathering" alerts.
#
# Usage: sudo ./scripts/run_port_scan.sh [TARGET_IP]

set -e

# --- Configuration ---
TARGET_IP=${1:-"127.0.0.1"}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Prerequisites ---
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[ERROR] Please run with sudo (required for SYN scans).${NC}"
    exit 1
fi
if ! command -v nmap >/dev/null 2>&1; then
    echo -e "${RED}[ERROR] 'nmap' is missing. Install it: sudo apt install nmap${NC}"
    exit 1
fi

# --- Setup ---
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}    NIDS DEMO: PORT SCAN ATTACK      ${NC}"
echo -e "${BLUE}=========================================${NC}"

echo -e "\n${GREEN}[1/2] Preparing scan against $TARGET_IP...${NC}"
echo ">> Dashboard Expectation: 'High' threat for 'Information Gathering'."
read -p "Press ENTER to launch scan..."

# 3. Launch Attack
echo -e "\n${RED}[2/2] LAUNCHING NMAP SYN SCAN!${NC}"
# -sS: TCP SYN Scan (Stealthy, does not complete handshake)
# -T4: Aggressive timing (faster scan for demo purposes)
# -n: No DNS resolution (speeds up scan, cleaner flows)
# -p 1-2000: Scan top 2000 ports (generates ~2000 flows quickly)
# --max-retries 1: Don't wait too long for filtered ports
nmap -sS -T4 -n -p 1-2000 --max-retries 1 "$TARGET_IP"

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}     SCAN FINISHED${NC}"
echo -e "${BLUE}=========================================${NC}"

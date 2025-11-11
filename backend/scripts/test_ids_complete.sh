#!/usr/bin/env bash
# test_ids_complete.sh
# Complete end-to-end testing workflow for IDS system
# Usage: sudo ./scripts/test_ids_complete.sh

set -eu

if [ "$EUID" -ne 0 ]; then
  echo "ERROR: Please run this script with sudo."
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# --- Configuration ---
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"
TEST_DIR="$REPO_ROOT/data/flows/test_results"
ORIGINAL_USER=${SUDO_USER:-$(whoami)}

# Temp files for Hydra
USERS_LIST="/tmp/ids_users.txt"
PASS_LIST="/tmp/ids_pass.txt"

# --- Trap for Cleanup ---
cleanup() {
    # Kill background jobs (listeners) if they are still running
    jobs -p | xargs -r kill 2>/dev/null || true
    rm -f "$USERS_LIST" "$PASS_LIST"
}
trap cleanup EXIT

# --- Pre-flight Checks ---
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python executable not found at $VENV_PYTHON"
    exit 1
fi

# Clean old tests
mkdir -p "$TEST_DIR"
echo "Cleaning old test files..."
rm -f "$TEST_DIR"/*.{pcap,csv,txt}

echo "========================================="
echo "IDS System Complete Testing (Targeted Demo)"
echo "========================================="
read -p "Press ENTER to start generation..."

# ==========================================
# 1. BENIGN TRAFFIC (Enhanced)
# ==========================================
echo ""
echo "-----------------------------------------"
echo "[1/4] Generating Benign Traffic (Web)"
echo "-----------------------------------------"
(
    for i in {1..20}; do
        curl -s https://www.example.com >/dev/null 2>&1 || true
        sleep $(( RANDOM % 3 ))
    done
) &
CURL_PID=$!
timeout 45 tcpdump -i lo -s 0 -w "$TEST_DIR/benign_web_https.pcap" 2>/dev/null || true
wait $CURL_PID 2>/dev/null || true

# ==========================================
# 2. MALICIOUS TRAFFIC
# ==========================================
for tool in nmap hping3 hydra; do
  if ! command -v $tool >/dev/null 2>&1; then
    echo "ERROR: Missing tool: $tool. Please install it."
    exit 1
  fi
done

echo ""
echo "-----------------------------------------"
echo "[2/4] Generating Malicious Traffic"
echo "-----------------------------------------"

# --- A. Port Scan ---
echo " > Generating: Information Gathering (SYN Scan)"
timeout 25 tcpdump -i lo -s 0 -w "$TEST_DIR/infogathering.pcap" 2>/dev/null &
TCPDUMP_PID=$!
sleep 2
nmap -sS -T4 -n --top-ports 1000 127.0.0.1 >/dev/null 2>&1 || true
sleep 2
kill -INT $TCPDUMP_PID 2>/dev/null || true
wait $TCPDUMP_PID 2>/dev/null || true

# --- B. DoS Attack (ACK Flood) ---
if command -v hping3 >/dev/null 2>&1; then
  echo "> Generating DoS traffic (ACK Flood)..."
  echo "(hping3 -A -i u100)"
  nc -l -p 9999 >/dev/null 2>&1 &
  NC_PID=$!
  sleep 1

  # -A = ACK Flood
  # -i u100 = 10,000 packets/sec.
  timeout 15 tcpdump -i lo -s 0 -w "$TEST_DIR/dos.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  timeout 10 hping3 -A -p 9999 -i u100 --rand-source 127.0.0.1 >/dev/null 2>&1 || true
  sleep 2

  kill -INT $TCPDUMP_PID 2>/dev/null || true
  wait $TCPDUMP_PID 2>/dev/null || true
  kill $NC_PID 2>/dev/null || true
fi

# --- C. Bruteforce (Hydra Multi-Service) ---
if command -v hydra >/dev/null 2>&1; then
  echo "Generating 'Bruteforce' traffic (Hydra simulation)..."
  timeout 90 tcpdump -i lo -s 0 -w "$TEST_DIR/bruteforce.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 2

  {
    echo "  -> Launching distributed brute-force attempts..."
    USERS="/tmp/users.txt"
    PASS="/tmp/pass.txt"
    echo -e "admin\nuser\nroot\ntest" > "$USERS"
    echo -e "1234\nadmin\npassword\nroot\nletmein" > "$PASS"

    TARGETS=(127.0.0.{2..7})
    SERVICES=(ssh ftp http-post)

    for svc in "${SERVICES[@]}"; do
      for tgt in "${TARGETS[@]}"; do
        hydra -L "$USERS" -P "$PASS" "$tgt" "$svc" \
          -t 4 -V -I -W 1 -f >/dev/null 2>&1 &
      done
    done

    wait
    sleep 2
    kill -INT $TCPDUMP_PID 2>/dev/null || true
  } &
  wait $!
  wait $TCPDUMP_PID 2>/dev/null || true
fi

# ==========================================
# 3. PROCESS & INFER
# ==========================================
echo ""
echo "-----------------------------------------"
echo "[3/4] Processing PCAPs to Flows"
echo "-----------------------------------------"
"$REPO_ROOT/scripts/process_pcaps.sh" "$TEST_DIR"

echo ""
echo "-----------------------------------------"
echo "[4/4] Running AI Inference"
echo "-----------------------------------------"
RESULTS_FILE="$TEST_DIR/report_$(date +%Y%m%d_%H%M%S).txt"
./scripts/run_inference.sh "$TEST_DIR" 2>/dev/null | tee "$RESULTS_FILE"

chown -R "$ORIGINAL_USER":"$ORIGINAL_USER" "$TEST_DIR"
echo ""
echo "Done. Full report saved to: $RESULTS_FILE"

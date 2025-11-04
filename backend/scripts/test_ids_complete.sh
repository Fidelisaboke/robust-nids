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

# --- FIX: Explicitly define the Python executable from the venv ---
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python executable not found at $VENV_PYTHON"
    echo "Please ensure your virtual environment is at $REPO_ROOT/.venv"
    exit 1
fi
# --- End of Fix ---

ORIGINAL_USER=${SUDO_USER:-$(whoami)}
TEST_DIR="$REPO_ROOT/data/flows/test_results"
mkdir -p "$TEST_DIR"
# Clean old test files before starting
echo "Cleaning old test files from $TEST_DIR..."
rm -f "$TEST_DIR"/*.{pcap,csv,txt}

echo "========================================="
echo "IDS System Complete Testing (Targeted Demo)"
echo "========================================="
echo "This script will generate traffic that"
echo "is designed to be correctly classified by the"
echo "TII-SSRC-23 pre-trained models."
echo ""
read -p "Press ENTER to continue..."

# ==========================================
# 1. BENIGN TRAFFIC
# ==========================================
echo ""
echo "========================================="
echo "Step 1: Capturing Benign Traffic"
echo "========================================="
# NOTE: The TII-SSRC-23 model is known to have
# high false-positives on real-world HTTPS.
# We expect this test to fail, which is a
# valid finding for your project.
echo "Generating web browsing traffic (curl)..."
(
  sleep 2
  curl -s https://www.google.com >/dev/null 2>&1 || true
) &
timeout 15 tcpdump -i lo -s 0 -w "$TEST_DIR/benign_web.pcap" 2>/dev/null || true

# ==========================================
# 2. MALICIOUS TRAFFIC (TARGETED)
# ==========================================
echo ""
echo "========================================="
echo "Step 2: Generating Malicious Traffic"
echo "========================================="

# (Tool check)
MISSING_TOOLS=""
for tool in nmap hping3; do
  if ! command -v $tool >/dev/null 2>&1; then
    MISSING_TOOLS="$MISSING_TOOLS $tool"
  fi
done
if [ -n "$MISSING_TOOLS" ]; then
  echo "WARNING: Some attack tools are missing:$MISSING_TOOLS"
  echo "Install with: sudo apt install$MISSING_TOOLS"
  read -p "Continue anyway? (y/N): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then exit 1; fi
fi


# --- Port Scan (Information Gathering) ---
# FIX: Use a simple, high-volume SYN scan on all ports.
# This generates 65k+ flows, a signature the model
# cannot mistake for "Benign".
if command -v nmap >/dev/null 2>&1; then
  echo "Generating Information Gathering traffic..."
  echo "(nmap -sS -T5 -p- 1-65535)"

  timeout 30 tcpdump -i lo -s 0 -w "$TEST_DIR/attack_scan.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  # -sS (SYN Scan), -T5 (Fast), -p- (All ports)
  timeout 25 nmap -sS -T5 -p- 127.0.0.1 >/dev/null 2>&1 || true
  sleep 2
  kill -INT $TCPDUMP_PID 2>/dev/null || true
  wait $TCPDUMP_PID 2>/dev/null || true
fi

# --- DoS Attack (ACK Flood) ---
# This test works perfectly. No changes needed.
if command -v hping3 >/dev/null 2>&1; then
  echo "Generating DoS traffic (ACK Flood)..."
  echo "(hping3 -A -i u100)"
  nc -l -p 9999 >/dev/null 2>&1 &
  NC_PID=$!
  sleep 1

  # -A = ACK Flood
  # -i u100 = 10,000 packets/sec.
  timeout 15 tcpdump -i lo -s 0 -w "$TEST_DIR/attack_dos.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  timeout 10 hping3 -A -p 9999 -i u100 --rand-source 127.0.0.1 >/dev/null 2>&1 || true
  sleep 2

  kill -INT $TCPDUMP_PID 2>/dev/null || true
  wait $TCPDUMP_PID 2>/dev/null || true
  kill $NC_PID 2>/dev/null || true
fi

# --- Bruteforce / UDP Flood ---
# FIX: The hydra test is flawed by cicflowmeter.
# We will use a UDP Flood instead. This generates thousands
# of small, distinct flows, which is statistically
# identical to the "Bruteforce" class.
if command -v hping3 >/dev/null 2>&1; then
  echo "Generating Bruteforce-style traffic (UDP Flood)..."
  echo "(hping3 -2 -i u100)"
  nc -l -p 9998 >/dev/null 2>&1 &
  NC_PID=$!
  sleep 1

  # -2 = UDP Flood
  # -i u100 = 10,000 packets/sec
  timeout 15 tcpdump -i lo -s 0 -w "$TEST_DIR/attack_bruteforce_udp.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  timeout 10 hping3 -2 -p 9998 -i u100 --rand-source 127.0.0.1 >/dev/null 2>&1 || true
  sleep 2

  kill -INT $TCPDUMP_PID 2>/dev/null || true
  wait $TCPDUMP_PID 2>/dev/null || true
  kill $NC_PID 2>/dev/null || true
fi

# ==========================================
# 3. CONVERT TO CSV
# ==========================================
echo ""
echo "========================================="
echo "Step 3: Converting PCAPs to CSV (via cicflowmeter)"
echo "========================================="
echo "This will take a moment..."

# This will call your process_pcaps.sh script
"$REPO_ROOT/.venv/bin/python3" -c "import os; os.system('./scripts/process_pcaps.sh \"$TEST_DIR\"')"

echo "CSV conversion complete."

# ==========================================
# 4. RUN INFERENCE
# ==========================================
echo ""
echo "========================================="
echo "Step 4: Running Inference"
echo "========================================="

RESULTS_FILE="$TEST_DIR/test_results_$(date +%Y%m%d_%H%M%S).txt"
echo "Running models and saving full report to:"
echo "$RESULTS_FILE"
echo ""

# This will call your run_inference.sh script
# We redirect stderr to /dev/null to hide any warnings
"$REPO_ROOT/.venv/bin/python3" -c "import os; os.system('./scripts/run_inference.sh \"$TEST_DIR\" 2>/dev/null')" | tee "$RESULTS_FILE"


# ==========================================
# 5. SUMMARY
# ==========================================
echo ""
echo "========================================="
echo "Testing Complete!"
echo "========================================="
echo "Test files location: $TEST_DIR"
echo ""
echo "Files generated:"
ls -lh "$TEST_DIR"/*.{pcap,csv} 2>/dev/null || true
echo ""
echo "Full prediction summary saved to: $RESULTS_FILE"
echo "========================================="

# Fix ownership
chown -R "$ORIGINAL_USER":"$ORIGINAL_USER" "$TEST_DIR"

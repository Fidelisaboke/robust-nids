#!/usr/bin/env bash
#
# generate_dataset.sh
#
# This script generates a large, high-quality, and correctly-labeled
# set of PCAP files for augmenting the TII-SSRC-23 dataset.
# It is designed to be run ONCE to create your new "golden" dataset.
#
# Usage: sudo ./scripts/generate_dataset.sh
#

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
LOG_FILE="$TEST_DIR/data_generation_log.txt"
mkdir -p "$TEST_DIR"

# --- Cleanup Trap ---
# Ensures that temp files and background processes are killed on exit/error
cleanup() {
    echo ""
    echo "--- Cleaning up background processes and temp files... ---"
    # Kill all background processes started by this script
    # pkill -P $$ will kill all child processes of the current script
    pkill -P $$ || true
    rm -f /tmp/sample_text.txt
    rm -f /tmp/testvideo.bin
    rm -f /tmp/testaudio.bin
    echo "Cleanup complete."
    # Fix ownership
    chown -R "$ORIGINAL_USER":"$ORIGINAL_USER" "$TEST_DIR" 2>/dev/null || true
}
trap cleanup EXIT

# --- Helper function for realistic text ---
create_lorem_file() {
    LOREM_FILE="/tmp/sample_text.txt"
    echo "Creating realistic 1M text file at $LOREM_FILE..."
    # A small block of sample text
    LOREM_IPSUM="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. "
    # Repeat the block ~220 times to get ~128KB
    for i in {1..220}; do
        echo $LOREM_IPSUM >> $LOREM_FILE
    done
}

# --- Helper function for progress indicator ---
spinner() {
    local pid=$1
    local msg=$2
    local delay=0.1
    local spinstr='|/-\'
    echo -n "$msg "
    while ps -p $pid > /dev/null; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf " [Done] \n"
}

# Clean old test files before starting
echo "Cleaning old test files from $TEST_DIR..."
rm -f "$TEST_DIR"/*.{pcap,csv,txt}

echo "========================================="
echo "IDS System - Augmentation Data Generation"
echo "========================================="
echo "This script will generate data for under-represented"
echo "classes (Benign, Info Gathering, Bruteforce)."
echo "This will take several minutes to meet the data quotas."
echo ""
read -p "Press ENTER to continue..."


# --- Benign-Web (Realistic Hybrid Simulation) ---
# Captures both high-volume local traffic and realistic external HTTPS.
# NOTE: Requires Internet access for external tests.
echo "Generating realistic web traffic (Hybrid Local/External)..."
(
  # Capture on lo and eth0
  timeout 600 tcpdump -i any -s 0 -w "$TEST_DIR/benign_web_https.pcap" 'not port 22' >/dev/null 2>&1 &
  TCPDUMP_PID=$!
  sleep 2
  {
    # 1. Start Local Noise Server (for volume)
    mkdir -p /tmp/www_noise
    echo "generic_data" > /tmp/www_noise/index.html
    python3 -m http.server 8080 --directory /tmp/www_noise >/dev/null 2>&1 &
    HTTP_PID=$!
    sleep 1

    # 2. Define Safe External Targets (for realism)
    # These provide real TLS handshakes and varied connection timings.
    EXT_TARGETS=(
        "https://www.example.com"
        "https://www.example.org"
        "https://www.example.net"
        "http://httpforever.com"
    )

    echo "  -> Starting hybrid browsing simulation (approx 10 mins)..."
    # Main loop - mixes local volume with intermittent external realism
    for i in {1..800}; do
        # A. High-Volume Local Hits (Fast background noise)
        for j in {1..4}; do
          curl -s "http://127.0.0.1:8080/sample_text.txt?resource=$j&session=$i" >/dev/null &
        done

        # B. Realistic External Hit (Slower, real TLS handshake)
        for k in {1..3}; do
          # We pick a random target from the list
          TARGET=${EXT_TARGETS[$RANDOM % ${#EXT_TARGETS[@]}]}
          # -L follows redirects (common in real traffic, e.g., 80->443)
          curl -s -L "$TARGET" -o /dev/null &
        done

        # C. AJAX-like request
        curl -s "http://127.0.0.1:8080/sample_text.txt?ajax=$i" -H "X-Requested-With: XMLHttpRequest" >/dev/null &

        # Jitter: sleep between 0.1s and 0.4s
        sleep "$(shuf -i 1-4 -n 1 | awk '{print $1/10}')"
    done

    # Wait for all curl background jobs in THIS subshell to finish
    wait

    # Cleanup local server immediately after loop
    kill $HTTP_PID 2>/dev/null || true
    sleep 2
    kill -INT $TCPDUMP_PID 2>/dev/null || true
  } &
  wait $!
  wait $TCPDUMP_PID 2>/dev/null || true
) &
spinner $! "  -> Generating 5,000+ 'Web' flows (hybrid local/external)..."


# --- Video Traffic (Realistic multi-stream) ---
echo "Generating 'Video' traffic (realistic streaming)..."
(
  timeout 75 tcpdump -i lo -s 0 -w "$TEST_DIR/benign_video.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  {
    echo "  -> Simulating multiplexed video streaming sessions..."
    # Generate dummy video payload
    dd if=/dev/urandom of=/tmp/testvideo.bin bs=1K count=200 >/dev/null 2>&1

    for session in {1..300}; do
      port=$((52000 + session))
      # Simulate video streaming bursts (HTTP progressive style)
      curl -s --limit-rate $((100 + RANDOM % 400))K \
        -T /tmp/testvideo.bin "http://127.0.0.1:$port/upload?stream=$session" >/dev/null 2>&1 &

      # Random jitter between clients
      sleep 0.$((RANDOM % 4))
      if (( session % 50 == 0 )); then wait; fi
    done
    wait

    echo "  -> Realistic video streaming complete"
    sleep 2
    kill -INT $TCPDUMP_PID 2>/dev/null || true
  } &
  wait $!
  wait $TCPDUMP_PID 2>/dev/null || true
) &
spinner $! "  -> Generating 2000+ 'Video' flows (progressive streaming)..."


# --- Audio Traffic (VoIP Simulation) ---
echo "Generating 'Audio' traffic (RTP-style UDP)..."
(
  timeout 70 tcpdump -i lo -s 0 -w "$TEST_DIR/benign_audio.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  {
    echo "  -> Simulating RTP/VoIP streams..."
    for call in {1..400}; do
      dst_port=$((53000 + (call % 50)))
      src_port=$((60000 + call))
      # 50–200 byte UDP bursts at 20–60 ms intervals
      for pkt in {1..20}; do
        head -c $((50 + RANDOM % 150)) /dev/urandom | \
          nc -u -w 0.02 -p $src_port 127.0.0.1 $dst_port >/dev/null 2>&1
        sleep 0.0$((2 + RANDOM % 5))
      done &
      if (( call % 80 == 0 )); then wait; fi
    done
    wait
    echo "  -> Audio streaming completed"
    sleep 2
    kill -INT $TCPDUMP_PID 2>/dev/null || true
  } &
  wait $!
  wait $TCPDUMP_PID 2>/dev/null || true
) &
spinner $! "  -> Generating 3,000+ 'Audio' flows (RTP-like UDP)..."



# --- Benign-Text (File Transfer) ---
# This traffic is realistic and has natural jitter.
# Expected Flows: ~3000
create_lorem_file
echo "Generating 'Text' traffic (file transfer)..."
python3 -m http.server 8000 --directory /tmp >/dev/null 2>&1 &
HTTP_PID=$!
(
  timeout 60 tcpdump -i lo 'port 8000' -s 0 -w "$TEST_DIR/benign_text.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1 # Wait for tcpdump to start
  {
    # Download a text-like file 3000 times
    for i in {1..3000}; do
      curl -s http://127.0.0.1:8000/sample_text.txt -o /dev/null || true
      # Add light timing jitter (0–0.3s)
      sleep 0.$((RANDOM % 3))
    done
    sleep 2
    kill -INT $TCPDUMP_PID 2>/dev/null || true
  } &
  wait $!
  wait $TCPDUMP_PID 2>/dev/null || true
) &
spinner $! "  -> Generating 3000 'Text' flows (curl loop)..."
kill $HTTP_PID 2>/dev/null || true

# --- Background (Natural Mix) ---
echo "Generating 'Background' traffic (natural mix)..."
(
  timeout 90 tcpdump -i lo -s 0 -w "$TEST_DIR/benign_background.pcap" 2>/dev/null &
  TCPDUMP_PID=$!
  sleep 1
  {
    echo "  -> Spawning DNS, HTTP, and ICMP chatter..."

    for i in {1..20000}; do
      case $((RANDOM % 4)) in
        0) # HTTP GET
          curl -s "http://localhost:8080/?id=$RANDOM" >/dev/null 2>&1 &
          ;;
        1) # DNS-like query
          echo "example$i.com" | nc -u -w 0.02 127.0.0.1 53 >/dev/null 2>&1 &
          ;;
        2) # ICMP ping
          ping -c 1 -i 0.05 127.0.0.1 >/dev/null 2>&1 &
          ;;
        3) # Random UDP chatter
          echo "bg$i" | nc -u -w 0.02 127.0.0.1 $((54000 + (RANDOM % 100))) >/dev/null 2>&1 &
          ;;
      esac
      if (( i % 2000 == 0 )); then wait; fi
    done
    wait
    echo "  -> Background chatter complete"
    sleep 1
    kill -INT $TCPDUMP_PID 2>/dev/null || true
  } &
  wait $!
  wait $TCPDUMP_PID 2>/dev/null || true
) &
spinner $! "  -> Generating 20,000+ 'Background' flows (mixed traffic)..."




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

# --- Information Gathering (Nmap Scan) ---
# Goal: ~14,000 unique flows (SYN, FIN, XMAS scans), smaller PCAP
if command -v nmap >/dev/null 2>&1; then
  echo "Generating 'Information Gathering' traffic (optimized)..."
  (
    timeout 45 tcpdump -i lo -s 0 -w "$TEST_DIR/infogathering.pcap" 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1 # Ensure tcpdump is running

    {
      echo "  -> Running lightweight mixed port scans..."

      # Target range (smaller subset, randomized hosts)
      TARGETS=(127.0.0.{2..5})
      PORT_RANGE="1-1000"
      SCAN_TYPES=(-sS -sF -sX)

      # Fewer scans per type, randomized timing for realism
      for scan in "${SCAN_TYPES[@]}"; do
        for target in "${TARGETS[@]}"; do
          # Limit rate and randomize hosts
          sudo nmap $scan -p $PORT_RANGE "$target" \
            --max-rate 1200 \
            --randomize-hosts \
            --defeat-rst-ratelimit \
            >/dev/null 2>&1 &
          sleep $((1 + RANDOM % 2))
        done
      done

      wait
      sleep 2
      kill -INT $TCPDUMP_PID 2>/dev/null || true
    } &

    wait $!
    wait $TCPDUMP_PID 2>/dev/null || true
  ) &

  spinner $! "  -> Generating ~14,000 'InfoGathering' flows (SYN/FIN/XMAS)..."
fi


# --- Bruteforce (Hydra + Mixed Protocols) ---
# Goal: 12,000+ unique flows, realistic login attempts
if command -v hydra >/dev/null 2>&1; then
  echo "Generating 'Bruteforce' traffic (Hydra simulation)..."
  (
    timeout 90 tcpdump -i lo -s 0 -w "$TEST_DIR/bruteforce.pcap" 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 2

    {
      echo "  -> Launching distributed brute-force attempts..."
      USERS="/tmp/users.txt"
      PASS="/tmp/pass.txt"
      echo -e "admin\nuser\nroot\ntest" > "$USERS"
      echo -e "1234\nadmin\npassword\nroot\nletmein" > "$PASS"

      TARGETS=(127.0.0.{2..6})
      SERVICES=(ssh ftp http-post smtp)

      for svc in "${SERVICES[@]}"; do
        for tgt in "${TARGETS[@]}"; do
          hydra -L "$USERS" -P "$PASS" "$tgt" "$svc" \
            -t 4 -V -I -W 1 -f >/dev/null 2>&1 &
          # Randomized delay to avoid identical timing
          sleep $((RANDOM % 3))
        done
      done

      wait
      echo "  -> Hydra brute-force generation completed"
      sleep 2
      kill -INT $TCPDUMP_PID 2>/dev/null || true
    } &
    wait $!
    wait $TCPDUMP_PID 2>/dev/null || true
  ) &
  spinner $! "  -> Generating 12,000+ 'Bruteforce' flows (multi-protocol)..."
fi



# --- DoS Attack (REMOVED) ---
echo "Skipping DoS generation (dataset is already over-represented)."
echo ""


# ==========================================
# 3. CONVERT TO CSV & LOG METADATA
# ==========================================
echo ""
echo "========================================="
echo "Step 3: Converting PCAPs to CSV (via cicflowmeter)"
echo "========================================="
echo "This will take several minutes..."

# --- FIX: Create log file header ---
START_TIME=$(date)
echo "=== Data Generation Log ===" > "$LOG_FILE"
echo "Run started: $START_TIME" >> "$LOG_FILE"
echo "Interface: lo (loopback)" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
echo "Flow Counts per CSV:" >> "$LOG_FILE"

# --- FIX: Pipe output of process_pcaps.sh to tee ---
# This will log to the file AND show on the console
if ! "$VENV_PYTHON" -c "import os; os.system('./scripts/process_pcaps.sh \"$TEST_DIR\"')" | tee -a "$LOG_FILE"; then
    echo "Error during CSV conversion."
    exit 1
fi

END_TIME=$(date)
echo "---" >> "$LOG_FILE"
echo "Run finished: $END_TIME" >> "$LOG_FILE"
# Calculate total duration
# We use python for a robust calculation.
"$VENV_PYTHON" -c "from datetime import datetime; \
    start_str = \"$START_TIME\"; \
    end_str = \"$END_TIME\"; \
    start = datetime.strptime(start_str, '%a %b %d %H:%M:%S %Z %Y'); \
    end = datetime.strptime(end_str, '%a %b %d %H:%M:%S %Z %Y'); \
    print(f'Total duration: {end - start}')" >> "$LOG_FILE"

echo ""
echo "CSV conversion complete."

# ==========================================
# 4. SUMMARY & CLEANUP
# ==========================================
echo ""
echo "========================================="
echo "Data Generation Complete!"
echo "========================================="
echo "Test files location: $TEST_DIR"
echo ""
echo "Files generated:"
ls -lh "$TEST_DIR"/*.{pcap,csv} 2>/dev/null || true
echo ""
echo "Log file saved to: $LOG_FILE"
echo "--- Log Contents ---"
cat "$LOG_FILE"
echo "--------------------"

# --- Cleanup Temp Files ---
# (Cleanup is now handled by the 'trap' at the top)
echo ""

# --- Next Step ---
echo "NEXT STEP: Upload all the new, renamed CSV files from"
echo "$TEST_DIR to your Colab notebook and run the"
echo "updated '03_preprocessing.ipynb' script to create your hybrid dataset."
echo "========================================="

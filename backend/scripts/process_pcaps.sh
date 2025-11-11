#!/usr/bin/env bash
#
# process_pcaps.sh
#
# Automatically finds all .pcap files in a directory, runs 'cicflowmeter'
# on them, renames the output to a consistent class name, and counts
# the generated flows.
#
# Usage:
#   Run from the repository root folder.
#   ./scripts/process_pcaps.sh [optional_directory]
#
#   If no directory is provided, it defaults to 'data/flows/test_results'.
#

set -eu

# --- Configuration ---
PCAP_DIR=${1:-"data/flows/test_results"}

# --- FIX: Find Python in the venv ---
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"

# --- Pre-run Checks ---

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python executable not found at $VENV_PYTHON"
    echo "Please ensure your virtual environment is at $REPO_ROOT/.venv"
    exit 1
fi

# Check if the module is installed by trying to import it
if ! "$VENV_PYTHON" -c "import cicflowmeter" &> /dev/null; then
    echo "Error: 'cicflowmeter' package not found in $VENV_PYTHON."
    echo "Please ensure it's installed in your venv (e.g., 'uv pip install cicflowmeter')"
    exit 1
fi

if [ ! -d "$PCAP_DIR" ]; then
    echo "Error: PCAP directory not found at $PCAP_DIR"
    exit 1
fi

# ==========================================
# HELPER: Smart Renaming Function
# ==========================================
# This function maps the generated PCAP filename to
# a clean, TII-SSRC-23 compatible class name.
get_output_name() {
    local pcap_filename=$1
    echo "$(basename "$pcap_filename" .pcap).csv"
}


# ==========================================
# Main Processing Loop
# ==========================================
find "$PCAP_DIR" -maxdepth 1 -type f -name "*.pcap" -print0 | while IFS= read -r -d '' pcap_file; do

    filename=$(basename "$pcap_file")

    # --- FIX: Get the new, clean output name ---
    output_name=$(get_output_name "$filename")
    output_csv="$PCAP_DIR/$output_name"

    echo "Processing: $filename"

    # Run cicflowmeter. We create a temp name first.
    temp_output_csv="${pcap_file%.pcap}_temp.csv"

    # Call cicflowmeter as a module, which is more robust
    "$VENV_PYTHON" -m cicflowmeter.sniffer \
        -f "$pcap_file" \
        -c \
        "$temp_output_csv" > /dev/null 2>&1 # Suppress cicflowmeter stdout

    # Rename the temp file to the final clean name
    mv "$temp_output_csv" "$output_csv"

    # Count flows and log it ---
    # wc -l includes the header, so subtract 1 for the true flow count
    flow_count=$(($(wc -l < "$output_csv") - 1))

    # This output will be captured by `tee` in the main script
    echo "  -> $output_name ($flow_count flows)"

done

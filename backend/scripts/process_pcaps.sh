#!/usr/bin/env bash
#
# process_pcaps.sh
#
# Automatically finds all .pcap files in a directory and runs
# the 'cicflowmeter' python tool on them.
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

echo "========================================="
echo "Batch PCAP to CSV Conversion (via CICFlowMeter)"
echo "========================================="
echo "Source Directory: $PCAP_DIR"
echo "Extractor:        $VENV_PYTHON -m cicflowmeter.sniffer"
echo ""

# --- Main Processing Loop ---
find "$PCAP_DIR" -maxdepth 1 -type f -name "*.pcap" -print0 | while IFS= read -r -d '' pcap_file; do

    filename=$(basename "$pcap_file")
    base_path="${pcap_file%.pcap}"
    output_csv="${base_path}_cicflowmeter.csv"

    echo "Processing: $filename"
    echo "  -> Generating CSV: $(basename "$output_csv")"

    # --- FIX: Call cicflowmeter as a Python module ---
    # This correctly uses the venv's python and finds the patched package.
    # We pass the output file as the *last* argument to avoid the "output required" error.
    "$VENV_PYTHON" -m cicflowmeter.sniffer \
        -f "$pcap_file" \
        -c \
        "$output_csv"

    echo "  Done."
    echo ""

done

echo "========================================="
echo "Conversion Complete."
echo "Generated CSVs are in $PCAP_DIR"
echo "========================================="

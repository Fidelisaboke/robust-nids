#!/usr/bin/env bash
#
# run_inference.sh
#
# Automatically finds all *_cicflowmeter.csv files in the test directory
# and runs the inference script on them for BOTH binary and multiclass.
#
# Usage:
#   Run from the repository root folder.
#   ./scripts/run_inference.sh [optional_directory]
#
#   If no directory is provided, it defaults to 'data/flows/test_results'.
#

set -eu

# --- Configuration ---
CSV_DIR=${1:-"data/flows/test_results"}

# --- FIX: Find Python in the venv ---
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"
INFERENCE_SCRIPT="$REPO_ROOT/ml/inference.py"

# --- Model & Feature Artifacts ---
ARTIFACTS_DIR="$REPO_ROOT/ml/models/artifacts"
BINARY_MODEL="$ARTIFACTS_DIR/binary_classifier.json"
BINARY_FEATURES="$ARTIFACTS_DIR/binary_features.json"
MULTICLASS_MODEL="$ARTIFACTS_DIR/multiclass_classifier.json"
MULTICLASS_FEATURES="$ARTIFACTS_DIR/multiclass_features.json"
LABEL_ENCODER="$ARTIFACTS_DIR/label_encoder.pkl"
BINARY_SCALER="$ARTIFACTS_DIR/binary_scaler.pkl"
MULTICLASS_SCALER="$ARTIFACTS_DIR/multiclass_scaler.pkl"

# --- Pre-run Checks ---

echo "========================================="
echo "Batch Inference Runner"
echo "========================================="

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Python executable not found at $VENV_PYTHON"
    echo "Please ensure your virtual environment is at $REPO_ROOT/.venv"
    exit 1
fi

if [ ! -f "$INFERENCE_SCRIPT" ]; then
    echo "Error: Inference script not found at $INFERENCE_SCRIPT"
    exit 1
fi

if [ ! -d "$CSV_DIR" ]; then
    echo "Error: CSV directory not found at $CSV_DIR"
    exit 1
fi

# Check for all required artifact files
for f in "$BINARY_MODEL" "$BINARY_FEATURES" "$MULTICLASS_MODEL" "$MULTICLASS_FEATURES" "$LABEL_ENCODER" "$BINARY_SCALER" "$MULTICLASS_SCALER"; do
    if [ ! -f "$f" ]; then
        echo "Error: Required artifact not found: $f"
        echo "Please update the configuration at the top of this script."
        exit 1
    fi
done

echo "CSV Directory:    $CSV_DIR"
echo "Inference Script: $INFERENCE_SCRIPT"
echo "Models Path:      $ARTIFACTS_DIR"
echo ""

# --- Main Processing ---

# Find all files ending in *.csv
find "$CSV_DIR" -maxdepth 1 -type f -name "*.csv" -print0 | while IFS= read -r -d '' csv_file; do
    echo ""
    echo "================ Testing: $(basename "$csv_file") ================"

    echo ""
    echo "--- Mode: BINARY ---"
    "$VENV_PYTHON" "$INFERENCE_SCRIPT" \
        --mode "binary" \
        --csv "$csv_file" \
        --features "$BINARY_FEATURES" \
        --model "$BINARY_MODEL" \
        --scaler "$BINARY_SCALER"

    echo ""
    echo "--- Mode: MULTICLASS ---"
    "$VENV_PYTHON" "$INFERENCE_SCRIPT" \
        --mode "multiclass" \
        --csv "$csv_file" \
        --features "$MULTICLASS_FEATURES" \
        --model "$MULTICLASS_MODEL" \
        --encoder "$LABEL_ENCODER" \
        --scaler "$MULTICLASS_SCALER"

    echo "==========================================================="
done

echo ""
echo "========================================="
echo "Inference Complete."
echo "========================================="

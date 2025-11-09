#!/usr/bin/env bash
#
# run_inference.sh
#
# Automatically finds all *.csv files in the designated directory
# and runs inference using Binary, Multiclass, and Unsupervised (Autoencoder) models.
#

set -eu

# --- Configuration ---
CSV_DIR=${1:-"data/flows/test_results"}
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"
INFERENCE_SCRIPT="$REPO_ROOT/ml/inference.py"
ARTIFACTS_DIR="$REPO_ROOT/ml/models/artifacts"

# --- Artifact Definitions ---
# Supervised
BINARY_PIPELINE="$ARTIFACTS_DIR/binary_xgboost.json"
MULTICLASS_PIPELINE="$ARTIFACTS_DIR/multiclass_pipeline.pkl"
LABEL_ENCODER="$ARTIFACTS_DIR/label_encoder.pkl"
BINARY_PREPROCESSOR="$ARTIFACTS_DIR/binary_preprocessor.pkl"

# Unsupervised (Autoencoder)
AE_MODEL="$ARTIFACTS_DIR/autoencoder_model.keras"
AE_PREPROCESSOR="$ARTIFACTS_DIR/unsupervised_pipeline.pkl"
AE_THRESHOLD="$ARTIFACTS_DIR/ae_threshold.txt"

# --- Pre-run Checks ---
echo "========================================="
echo "AI Security - Batch Inference Runner"
echo "========================================="

# Validate Environment
for f in "$VENV_PYTHON" "$INFERENCE_SCRIPT"; do
    if [ ! -f "$f" ]; then echo "Error: Missing critical file: $f"; exit 1; fi
done
if [ ! -d "$CSV_DIR" ]; then echo "Error: CSV directory not found at $CSV_DIR"; exit 1; fi

# Validate Artifacts
REQUIRED_ARTIFACTS=("$BINARY_PIPELINE" "$MULTICLASS_PIPELINE" "$LABEL_ENCODER" "$AE_MODEL" "$AE_PREPROCESSOR" "$AE_THRESHOLD")
for f in "${REQUIRED_ARTIFACTS[@]}"; do
    if [ ! -f "$f" ]; then echo "Error: Missing artifact: $f"; exit 1; fi
done

echo "Inference Engine Ready."
echo "Scanning: $CSV_DIR"
echo ""

# --- Main Processing Loop ---
find "$CSV_DIR" -maxdepth 1 -type f -name "*.csv" -print0 | while IFS= read -r -d '' csv_file; do
    echo "-----------------------------------------------------------"
    echo "TARGET: $(basename "$csv_file")"
    echo "-----------------------------------------------------------"

    # 1. Binary Pass (Fast Filter)
    "$VENV_PYTHON" "$INFERENCE_SCRIPT" \
        --mode binary \
        --csv "$csv_file" \
        --model "$BINARY_PIPELINE" \
        --preprocessor "$BINARY_PREPROCESSOR"

    # 2. Multiclass Pass (Detailed Forensics)
    "$VENV_PYTHON" "$INFERENCE_SCRIPT" \
        --mode multiclass \
        --csv "$csv_file" \
        --model "$MULTICLASS_PIPELINE" \
        --encoder "$LABEL_ENCODER"

    # 3. Unsupervised Pass (Zero-Day Detection)
    "$VENV_PYTHON" "$INFERENCE_SCRIPT" \
        --mode unsupervised \
        --csv "$csv_file" \
        --model "$AE_MODEL" \
        --preprocessor "$AE_PREPROCESSOR" \
        --threshold "$AE_THRESHOLD"

    echo ""
done

echo "Batch Inference Complete."

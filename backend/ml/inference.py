"""
Terminal-based traffic inferencing using full scikit-learn Pipelines and Autoencoders.
"""

import argparse
import os
import sys
from collections import Counter

import joblib
import numpy as np
import pandas as pd

from utils.constants import CICFLOWMETER_TO_TII_MAPPING

# Suppress TensorFlow info/warning messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

def preprocess_dataframe(df):
    """
    Preprocesses raw CICFlowMeter data to exactly match the training pipeline's expected input.
    """
    df.columns = [c.lower() for c in df.columns]
    df.rename(columns=CICFLOWMETER_TO_TII_MAPPING, inplace=True)

    # Explicit Protocol One-Hot Encoding
    if "Protocol" in df.columns:
        df["Protocol"] = pd.to_numeric(df["Protocol"], errors="coerce").fillna(-1)
        df["Protocol_6"] = (df["Protocol"] == 6).astype(float)
        df["Protocol_17"] = (df["Protocol"] == 17).astype(float)
        df["Protocol_0"] = (df["Protocol"] == 0).astype(float)
        df.drop(columns=["Protocol"], inplace=True)
    else:
        df["Protocol_6"] = 0.0
        df["Protocol_17"] = 0.0
        df["Protocol_0"] = 0.0

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)
    return df


# --- CLI Setup ---
parser = argparse.ArgumentParser(description="Run AI traffic inference.")
parser.add_argument(
    "--mode",
    type=str,
    choices=["binary", "multiclass", "unsupervised"],
    required=True,
    help="Inference mode.",
)
parser.add_argument("--csv", type=str, required=True, help="Path to input CSV.")
parser.add_argument(
    "--model", type=str, required=True, help="Path to model file (.pkl pipeline or .keras model)."
)
parser.add_argument("--encoder", type=str, help="Label encoder .pkl (Required for multiclass).")
parser.add_argument("--preprocessor", type=str, help="Preprocessor .pkl (Required for .json/.keras models)")
parser.add_argument("--threshold", type=str, help="Threshold .txt file (Required for unsupervised).")

args = parser.parse_args()

# --- Execution ---
try:
    # 1. Load and Preprocess Data
    print(f"Loading data: {args.csv}")
    raw_df = pd.read_csv(args.csv)
    if raw_df.empty:
        sys.exit("Error: Input CSV is empty.")
    df_clean = preprocess_dataframe(raw_df)

    model_ext = os.path.splitext(args.model)[1]
    is_pipeline = model_ext == ".pkl"

    # --- Model Loading & Data Prep ---
    if is_pipeline:
        # Case 1: Full Pipeline (Easiest, Preferred)
        print(f"Loading pipeline: {args.model}")
        model = joblib.load(args.model)
        X_ready = df_clean  # Pipeline handles scaling internally
    else:
        # Case 2: Raw Model (needs manual preprocessing)
        if not args.preprocessor:
            sys.exit(f"Error: Raw {model_ext} models require --preprocessor.")
        print(f"Loading preprocessor: {args.preprocessor}")
        preprocessor = joblib.load(args.preprocessor)
        X_ready = preprocessor.transform(df_clean)

        if model_ext == ".json":
            from xgboost import XGBClassifier

            model = XGBClassifier()
            model.load_model(args.model)
            print(f"Loaded XGBoost model: {args.model}")
        elif model_ext == ".keras":
            import tensorflow as tf
            model = tf.keras.models.load_model(args.model, compile=False)
            print(f"Loaded Keras model: {args.model}")

    # --- Inference Modes ---
    print(f"Running {args.mode.upper()} inference...")

    # --- UNSUPERVISED MODE (Autoencoder) ---
    if args.mode == "unsupervised":
        # Lazy import TensorFlow to save time for other modes
        import tensorflow as tf

        if not args.preprocessor or not args.threshold:
            sys.exit("Error: --preprocessor and --threshold required for unsupervised mode.")

        print(f"Loading preprocessor: {args.preprocessor}")
        preprocessor = joblib.load(args.preprocessor)

        print(f"Loading Keras model: {args.model}")
        model = tf.keras.models.load_model(args.model, compile=False)

        with open(args.threshold, "r") as f:
            threshold = float(f.read().strip())
        print(f"Loaded anomaly threshold: {threshold}")

        print("Running unsupervised inference...")
        # 1. Scale data using the exact same preprocessor as training
        X_scaled = preprocessor.transform(df_clean)
        # 2. Get reconstructions
        reconstructions = model.predict(X_scaled, verbose=0)
        # 3. Calculate MAE (Reconstruction Error)
        mae = np.mean(np.abs(X_scaled - reconstructions), axis=1)
        # 4. Compare to threshold (MAE > threshold = Anomaly/Malicious)
        labels = ["Anomaly (Malicious)" if error > threshold else "Benign" for error in mae]
    else:
        # Supervised (Binary/Multiclass)
        raw_preds = model.predict(X_ready)

        if args.mode == "binary":
            labels = ["Benign" if p == 0 else "Malicious" for p in raw_preds]
        elif args.mode == "multiclass":
            if not args.encoder:
                sys.exit("Error: Multiclass requires --encoder.")
            le = joblib.load(args.encoder)
            labels = le.inverse_transform(raw_preds)

    # 5. Output Summary
    print("\n=== Inference Summary ===")
    print(f"Mode: {args.mode.upper()}")
    print(f"Total Flows: {len(labels)}")
    counts = Counter(labels)
    for label, count in counts.most_common():
        print(f" - {label:<25}: {count:>6} ({(count / len(labels)) * 100:.1f}%)")

except Exception as e:
    print(f"\nAn unexpected error occurred:\n{e}")
    sys.exit(1)

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

# Suppress TensorFlow info/warning messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# --- Feature Name Mapping ---
CICFLOWMETER_TO_TII_MAPPING = {
    "flow_duration": "Flow Duration",
    "flow_byts_s": "Flow Bytes/s",
    "flow_pkts_s": "Flow Packets/s",
    "flow_iat_mean": "Flow IAT Mean",
    "flow_iat_max": "Flow IAT Max",
    "flow_iat_min": "Flow IAT Min",
    "flow_iat_std": "Flow IAT Std",
    "fwd_pkts_s": "Fwd Packets/s",
    "tot_fwd_pkts": "Total Fwd Packet",
    "totlen_fwd_pkts": "Total Length of Fwd Packet",
    "fwd_pkt_len_max": "Fwd Packet Length Max",
    "fwd_pkt_len_min": "Fwd Packet Length Min",
    "fwd_pkt_len_mean": "Fwd Packet Length Mean",
    "fwd_pkt_len_std": "Fwd Packet Length Std",
    "fwd_iat_tot": "Fwd IAT Total",
    "fwd_iat_max": "Fwd IAT Max",
    "fwd_iat_min": "Fwd IAT Min",
    "fwd_iat_mean": "Fwd IAT Mean",
    "fwd_iat_std": "Fwd IAT Std",
    "fwd_psh_flags": "Fwd PSH Flags",
    "fwd_urg_flags": "Fwd URG Flags",
    "fwd_header_len": "Fwd Header Length",
    "fwd_act_data_pkts": "Fwd Act Data Pkts",
    "fwd_seg_size_min": "Fwd Seg Size Min",
    "fwd_seg_size_avg": "Fwd Segment Size Avg",
    "bwd_pkts_s": "Bwd Packets/s",
    "tot_bwd_pkts": "Total Bwd packets",
    "totlen_bwd_pkts": "Total Length of Bwd Packet",
    "bwd_pkt_len_max": "Bwd Packet Length Max",
    "bwd_pkt_len_min": "Bwd Packet Length Min",
    "bwd_pkt_len_mean": "Bwd Packet Length Mean",
    "bwd_pkt_len_std": "Bwd Packet Length Std",
    "bwd_iat_tot": "Bwd IAT Total",
    "bwd_iat_max": "Bwd IAT Max",
    "bwd_iat_min": "Bwd IAT Min",
    "bwd_iat_mean": "Bwd IAT Mean",
    "bwd_iat_std": "Bwd IAT Std",
    "bwd_psh_flags": "Bwd PSH Flags",
    "bwd_urg_flags": "Bwd URG Flags",
    "bwd_header_len": "Bwd Header Length",
    "bwd_seg_size_min": "Bwd Seg Size Min",
    "bwd_seg_size_avg": "Bwd Segment Size Avg",
    "fin_flag_cnt": "FIN Flag Count",
    "syn_flag_cnt": "SYN Flag Count",
    "rst_flag_cnt": "RST Flag Count",
    "psh_flag_cnt": "PSH Flag Count",
    "ack_flag_cnt": "ACK Flag Count",
    "urg_flag_cnt": "URG Flag Count",
    "cwr_flag_count": "CWR Flag Count",
    "ece_flag_cnt": "ECE Flag Count",
    "down_up_ratio": "Down/Up Ratio",
    "pkt_size_avg": "Average Packet Size",
    "pkt_len_max": "Packet Length Max",
    "pkt_len_min": "Packet Length Min",
    "pkt_len_mean": "Packet Length Mean",
    "pkt_len_std": "Packet Length Std",
    "pkt_len_var": "Packet Length Variance",
    "init_fwd_win_byts": "FWD Init Win Bytes",
    "init_bwd_win_byts": "Bwd Init Win Bytes",
    "fwd_byts_b_avg": "Fwd Bytes/Bulk Avg",
    "fwd_pkts_b_avg": "Fwd Packet/Bulk Avg",
    "fwd_blk_rate_avg": "Fwd Bulk Rate Avg",
    "bwd_byts_b_avg": "Bwd Bytes/Bulk Avg",
    "bwd_pkts_b_avg": "Bwd Packet/Bulk Avg",
    "bwd_blk_rate_avg": "Bwd Bulk Rate Avg",
    "subflow_fwd_pkts": "Subflow Fwd Packets",
    "subflow_fwd_byts": "Subflow Fwd Bytes",
    "subflow_bwd_pkts": "Subflow Bwd Packets",
    "subflow_bwd_byts": "Subflow Bwd Bytes",
    "active_max": "Active Max",
    "active_min": "Active Min",
    "active_mean": "Active Mean",
    "active_std": "Active Std",
    "idle_max": "Idle Max",
    "idle_min": "Idle Min",
    "idle_mean": "Idle Mean",
    "idle_std": "Idle Std",
    "src_port": "Src Port",
    "dst_port": "Dst Port",
}


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

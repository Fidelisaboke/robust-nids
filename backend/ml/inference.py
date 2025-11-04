"""Terminal-based traffic inferencing for binary and multiclass models."""

import argparse
import json
import sys
from collections import Counter

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

# --- Feature Name Mapping ---
# Renames columns from cicflowmeter (left) to what the model expects (right)
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
    "fwd_seg_size_avg": "Fwd Seg Size Avg",
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
    "fwd_pkts_b_avg": "Fwd Packets/Bulk Avg",
    "fwd_blk_rate_avg": "Fwd Bulk Rate Avg",
    "bwd_byts_b_avg": "Bwd Bytes/Bulk Avg",
    "bwd_pkts_b_avg": "Bwd Packets/Bulk Avg",
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
}


def preprocess_dataframe(df):
    """
    Preprocesses the raw CICFlowMeter dataframe to match the training format.
    1. Renames columns
    2. Creates 'Protocol_6.0'
    3. Handles Infs and NaNs
    """
    # 1. Create 'Protocol_6.0' feature (TCP)
    # Check if 'protocol' column exists before creating the one-hot
    if "protocol" in df.columns:
        df["Protocol_6.0"] = (df["protocol"] == 6).astype(int)

    # 2. Rename columns to match model's expected feature names
    df.rename(columns=CICFLOWMETER_TO_TII_MAPPING, inplace=True)

    # 3. Handle infinities and NaNs
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    return df


# --- Setup Command-Line Argument Parsing ---
parser = argparse.ArgumentParser(description="Run traffic inferencing from the terminal.")

parser.add_argument(
    "--mode",
    type=str,
    choices=["binary", "multiclass"],
    required=True,
    help="Classification mode: 'binary' or 'multiclass'.",
)
parser.add_argument(
    "--csv", type=str, required=True, help="Path to the input CSV file containing traffic data."
)
parser.add_argument(
    "--features", type=str, required=True, help="Path to the JSON file listing the features to use."
)
parser.add_argument("--model", type=str, required=True, help="Path to the trained .pkl or .json model file.")
parser.add_argument(
    "--encoder", type=str, help="Path to the .pkl label encoder file (REQUIRED for multiclass mode)."
)
# --- FIX: Add the --scaler argument ---
parser.add_argument("--scaler", type=str, required=True, help="Path to the .pkl scaler file.")

# Parse the arguments
args = parser.parse_args()

# --- Load Data and Model using CLI Arguments ---

try:
    # Load features from CSV
    print(f"Loading data from: {args.csv}")
    df = pd.read_csv(args.csv)

    # Handle empty CSV files
    if df.empty:
        print("Warning: CSV file is empty. No predictions to make.")
        sys.exit(0)

    # Preprocess the dataframe (rename cols, create Protocol_6.0, etc.)
    df = preprocess_dataframe(df)

    # Load the feature list
    print(f"Loading features from: {args.features}")
    with open(args.features) as f:
        features = json.load(f)

    # Ensure all features are in the DataFrame *after* preprocessing
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print("\nError: The following required features are missing from the CSV after preprocessing:")
        print(missing_features)
        sys.exit(1)  # Exit the script with an error code

    # Select only the features the model was trained on
    X_unscaled = df[features]

    print(f"Loading scaler from: {args.scaler}")
    scaler = joblib.load(args.scaler)

    # Apply the scaler transformation
    X = scaler.transform(X_unscaled)

    # Load model
    print(f"Loading model from: {args.model}")
    if args.model.endswith(".json"):
        xgb_model = XGBClassifier()
        xgb_model.load_model(args.model)
        model = xgb_model
    else:
        model = joblib.load(args.model)

except FileNotFoundError as e:
    print("\nError: File not found.")
    print(e)
    sys.exit(1)
except Exception as e:
    print(f"\nAn error occurred during loading: {e}")
    sys.exit(1)


# --- Run Prediction Based on Mode ---
print("Running predictions...")

if args.mode == "binary":
    # Predict on the *scaled* data
    preds = model.predict(X)
    # Convert predictions numpy array to labels
    labels = ["Benign" if p == 0 else "Malicious" for p in preds]

    # --- Output Binary Summary ---
    total_flows = len(labels)
    label_counts = Counter(labels)

    print("\n--- Prediction Summary ---")
    print(f"Total Flows: {total_flows}")
    for label, count in label_counts.most_common():
        percentage = (count / total_flows) * 100
        print(f"  - {label}: {count} ({percentage:.2f}%)")

elif args.mode == "multiclass":
    # Check if encoder path was provided
    if not args.encoder:
        print("\nError: --encoder argument is required for multiclass mode.")
        sys.exit(1)

    try:
        # Load label encoder
        print(f"Loading label encoder from: {args.encoder}")
        label_encoder = joblib.load(args.encoder)
    except FileNotFoundError:
        print(f"\nError: Label encoder file not found at {args.encoder}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred loading the encoder: {e}")
        sys.exit(1)

    # Predict on the *scaled* data
    preds = model.predict(X)
    pred_labels = label_encoder.inverse_transform(preds).tolist()

    # --- Output Multiclass Summary ---
    total_flows = len(pred_labels)
    label_counts = Counter(pred_labels)

    print("\n--- Prediction Summary ---")
    print(f"Total Flows: {total_flows}")
    # Sort by count (most common first)
    for label, count in label_counts.most_common():
        percentage = (count / total_flows) * 100
        print(f"  - {label}: {count} ({percentage:.2f}%)")

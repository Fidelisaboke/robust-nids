from datetime import datetime

import numpy as np
import pandas as pd

from ml.models.loader import MODEL_BUNDLE

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


def _prepare_dataframe(features: dict) -> pd.DataFrame:
    """
    Converts raw input dict into a clean DataFrame matching training expectations.
    Handles column renaming, protocol One-Hot Encoding, and basic sanitization.
    """
    # 1. Create initial DataFrame
    df = pd.DataFrame([features])

    # 2. Standardize column names (lowercase -> map to TII names)
    df.columns = [c.lower() for c in df.columns]
    df.rename(columns=CICFLOWMETER_TO_TII_MAPPING, inplace=True)

    # 3. Explicit Protocol One-Hot Encoding
    # We must ensure these columns exist even if the specific protocol isn't in this single flow.
    # We use .get() on the original features dict if 'Protocol' or 'protocol' exists there,
    # or check the dataframe if it was already mapped.

    # Try to find protocol value from various common keys
    raw_proto = features.get("protocol") or features.get("Protocol") or df.get("Protocol", [None])[0]

    try:
        proto_val = int(raw_proto) if raw_proto is not None else -1
    except (ValueError, TypeError):
        proto_val = -1

    df["Protocol_6"] = 1.0 if proto_val == 6 else 0.0  # TCP
    df["Protocol_17"] = 1.0 if proto_val == 17 else 0.0  # UDP
    df["Protocol_0"] = 1.0 if proto_val == 0 else 0.0  # HOPOPT

    # Drop original protocol column if it exists to avoid confusion
    if "Protocol" in df.columns:
        df.drop(columns=["Protocol"], inplace=True)

    # 4. Sanitization (Inf/NaN)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    return df


def predict_full_report(features: dict) -> dict:
    """Runs all three models and synthesizes a unified security report."""
    if not MODEL_BUNDLE.loaded:
        raise RuntimeError("Models not loaded.")

    # Use the new robust preparation function
    df = _prepare_dataframe(features)
    bundle = MODEL_BUNDLE

    # --- 1. Binary Classification ---
    bin_pred, bin_proba = bundle.get_binary_prediction(df)
    bin_conf = bin_proba[bin_pred]

    bin_res = {
        "label": "Malicious" if bin_pred == 1 else "Benign",
        "confidence": float(bin_conf),
        "is_malicious": bool(bin_pred == 1),
    }

    # --- 2. Multiclass Classification ---
    multi_pred_idx, multi_proba = bundle.get_multiclass_prediction(df)

    top_3_indices = np.argsort(multi_proba)[-3:][::-1]
    classes = bundle.label_encoder.classes_
    top_3_probs = {classes[i]: float(multi_proba[i]) for i in top_3_indices}

    multi_res = {
        "label": bundle.label_encoder.inverse_transform([multi_pred_idx])[0],
        "confidence": float(multi_proba[multi_pred_idx]),
        "probabilities": top_3_probs,
    }

    # --- 3. Unsupervised (Anomaly) ---
    ae_input = bundle.unsupervised_pipeline.transform(df)
    ae_output = bundle.autoencoder.predict(ae_input, verbose=0)
    mae = np.mean(np.abs(ae_input - ae_output), axis=1)[0]

    anom_res = {
        "is_anomaly": bool(mae > bundle.ae_threshold),
        "anomaly_score": float(mae),
        "threshold": bundle.ae_threshold,
    }

    # --- 4. Synthesize Threat Level ---
    threat_level = "Low"
    if bin_res["is_malicious"]:
        threat_level = "High"
        if multi_res["label"] in ["Bruteforce", "DoS", "Mirai"]:
            threat_level = "Critical"
    elif anom_res["is_anomaly"]:
        threat_level = "Medium"

    return {
        "timestamp": datetime.now().isoformat(),
        "binary": bin_res,
        "multiclass": multi_res,
        "anomaly": anom_res,
        "threat_level": threat_level,
    }

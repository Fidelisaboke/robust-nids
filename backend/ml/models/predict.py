import logging
from datetime import datetime

import numpy as np
import pandas as pd

from ml.models.adversarial import generate_fgsm_samples
from ml.models.loader import MODEL_BUNDLE
from schemas.nids import RobustnessDemoResponse, RobustnessDemoResult
from utils.constants import CICFLOWMETER_TO_TII_MAPPING, MALICIOUS_LABELS, MODEL_FEATURE_ORDER

app_logger = logging.getLogger("uvicorn.error")


def _prepare_dataframe(features: dict) -> pd.DataFrame:
    """
    Converts raw input dict into a clean DataFrame matching training expectations.
    Handles column renaming, protocol One-Hot Encoding, and basic sanitization.
    """
    # 1. Create initial DataFrame
    df = pd.DataFrame([features])

    # 2. Standardize and Rename Columns FIRST
    df.columns = [c.lower() for c in df.columns]
    df.rename(columns=CICFLOWMETER_TO_TII_MAPPING, inplace=True)

    # 3. Identify Protocol (using the NEW standardized names)
    # Try finding it in the dataframe first, fallback to raw features if needed
    raw_proto = df.get("Protocol", [features.get("protocol")])[0]
    try:
        proto_val = int(raw_proto) if raw_proto is not None else -1
    except Exception:
        proto_val = -1

    # Handle Loopback Artifact (2048 = 0x0800 IPv4)
    if proto_val == 2048:
        # Use the STANDARDIZED column names for the check
        syn = df.get("SYN Flag Count", [0])[0]
        ack = df.get("ACK Flag Count", [0])[0]
        rst = df.get("RST Flag Count", [0])[0]
        fin = df.get("FIN Flag Count", [0])[0]

        is_tcp = syn > 0 or ack > 0 or rst > 0 or fin > 0
        proto_val = 6 if is_tcp else 17
        # print(f"DEBUG: Fixed Protocol 2048 -> {proto_val} (TCP flags found: {is_tcp})")

    # 4. Set OHE Protocol Columns
    df["Protocol_6"] = 1.0 if proto_val == 6 else 0.0
    df["Protocol_17"] = 1.0 if proto_val == 17 else 0.0
    df["Protocol_0"] = 1.0 if proto_val == 0 else 0.0

    if "Protocol" in df.columns:
        df.drop(columns=["Protocol"], inplace=True)

    # 5. Final Sanitization & Ordering
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    # Ensure exact column order matches training
    df = df.reindex(columns=MODEL_FEATURE_ORDER, fill_value=0)

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
        # CASE A: Binary model flagged it. Mark as medium-level threat.
        threat_level = "Medium"
        if multi_res["label"] in MALICIOUS_LABELS:
            # If Multiclass also detects a critical attack type, elevate to Critical.
            threat_level = "Critical"
        elif anom_res["is_anomaly"]:
            # If Autoencoder also flags it, elevate to High.
            threat_level = "High"
    elif anom_res["is_anomaly"]:
        # CASE B: Binary missed it, but Autoencoder flagged it.
        # Check if Multiclass also detects something suspicious.
        if multi_res["label"] in MALICIOUS_LABELS:
            # Two out of three models agree it looks bad -> ELEVATE to High.
            threat_level = "High"
        else:
            # Only AE flagged it -> Keep as Medium (Suspicious)
            threat_level = "Medium"

    # Get source and destination IPs for reporting
    src_ip = features.get("src_ip") or features.get("Src IP") or "unknown"
    dst_ip = features.get("dst_ip") or features.get("Dst IP") or "unknown"

    return {
        "timestamp": datetime.now().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "binary": bin_res,
        "multiclass": multi_res,
        "anomaly": anom_res,
        "threat_level": threat_level,
    }


def run_robustness_demo_experiment(features: dict) -> RobustnessDemoResponse:
    """
    Runs a live A/B/C test on a single flow to demonstrate model robustness.
    """
    bundle = MODEL_BUNDLE
    if not (bundle.vulnerable_binary_model and bundle.surrogate_model and bundle.binary_preprocessor):
        raise RuntimeError("Adversarial demo models are not loaded. Check server logs.")

    try:
        # --- 1. Prepare Data ---
        df_raw = _prepare_dataframe(features)
        X_scaled = bundle.binary_preprocessor.transform(df_raw)

        # --- 2. Generate Adversarial Sample ---
        # We are attacking a Malicious sample (1) to make it look Benign (0)
        y_target = np.zeros(1)  # Target is class 0
        epsilon = 0.1  # Standard epsilon for demo

        X_adv_tensor = generate_fgsm_samples(bundle.surrogate_model, X_scaled, y_target, epsilon=epsilon)
        X_adv_numpy = X_adv_tensor.numpy()

        # --- 3. Run Predictions ---
        results = []

        # Test 1: Vulnerable Model vs. Normal Flow
        pred_vuln_normal = bundle.vulnerable_binary_model.predict(X_scaled)[0]
        proba_vuln_normal = bundle.vulnerable_binary_model.predict_proba(X_scaled)[0]
        results.append(
            RobustnessDemoResult(
                model_name="Baseline (Vulnerable)",
                input_type="Normal Flow",
                predicted_label="Malicious" if pred_vuln_normal == 1 else "Benign",
                confidence=float(proba_vuln_normal[pred_vuln_normal]),
            )
        )

        # Test 2: Vulnerable Model vs. Adversarial Flow
        pred_vuln_adv = bundle.vulnerable_binary_model.predict(X_adv_numpy)[0]
        proba_vuln_adv = bundle.vulnerable_binary_model.predict_proba(X_adv_numpy)[0]
        results.append(
            RobustnessDemoResult(
                model_name="Baseline (Vulnerable)",
                input_type="Adversarial Flow (FGSM)",
                predicted_label="Malicious" if pred_vuln_adv == 1 else "Benign",
                confidence=float(proba_vuln_adv[pred_vuln_adv]),
            )
        )

        # Test 3: Robust Model vs. Adversarial Flow
        # Check how the robust model was loaded (pipeline or native)
        if bundle.binary_preprocessor:
            pred_robust_adv = bundle.binary_model.predict(X_adv_numpy)[0]
            proba_robust_adv = bundle.binary_model.predict_proba(X_adv_numpy)[0]
        else:
            app_logger.warning("Robust model is full pipeline, demo may be inaccurate.")
            pred_robust_adv, proba_robust_adv = bundle.get_binary_prediction(df_raw)

        results.append(
            RobustnessDemoResult(
                model_name="Adversarial-Trained (Robust)",
                input_type="Adversarial Flow (FGSM)",
                predicted_label="Malicious" if pred_robust_adv == 1 else "Benign",
                confidence=float(proba_robust_adv[pred_robust_adv]),
            )
        )

        return RobustnessDemoResponse(
            results=results,
            adversarial_sample_preview=(f"Epsilon {epsilon} applied. Vector[0:5]: {X_adv_numpy[0, :5]}"),
        )

    except Exception as e:
        app_logger.error(f"Robustness demo failed: {e}", exc_info=True)
        # Re-raise the exception to be caught by the router
        raise e

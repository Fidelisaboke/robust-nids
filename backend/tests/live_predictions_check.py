import os

import pandas as pd
import requests

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/api/v1/nids"
PREDICT_URL = f"{BASE_URL}/predict/full"
EXPLAIN_URL = f"{BASE_URL}/explain/binary"

# Paths
CURRENT_DIR = os.path.dirname(__file__)
RELATIVE_DATA_PATH = "../../backend/data/flows/test_results"
TEST_DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, RELATIVE_DATA_PATH))


def get_random_sample(filename):
    """Reads a random row from a CSV and returns it as a dictionary."""
    filepath = os.path.join(TEST_DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[WARN] File not found: {filepath}")
        return None

    try:
        df = pd.read_csv(filepath)
        if df.empty:
            print(f"[WARN] File is empty: {filename}")
            return None

        # Pick one random row and convert to dict
        return df.sample(1).to_dict(orient="records")[0]
    except Exception as e:
        print(f"[ERROR] Reading {filename}: {e}")
        return None


def test_prediction(sample, expected_type):
    """Tests the full prediction endpoint."""
    if sample is None:
        return

    print(f"\n-> Sending {expected_type} sample to PREDICT API...")
    try:
        response = requests.post(PREDICT_URL, json={"features": sample}, timeout=5)
        if response.status_code == 200:
            res = response.json()
            threat = res["threat_level"]
            print("\n[SUCCESS] Prediction received.")
            print(f"   - Threat Level: [{threat}]")
            print(f"   - Binary:       {res['binary']['label']} ({res['binary']['confidence']:.4f})")
            print(
                f"   - Multiclass:   {res['multiclass']['label']} "
                f"({res['multiclass']['confidence']:.4f})"
            )
        else:
            print(f"\n[FAIL] API Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"\n[FAIL] Request failed: {e}")


def test_explanation(sample, expected_type):
    """Tests the SHAP explanation endpoint."""
    if sample is None:
        return

    print(f"\n-> Sending {expected_type} sample to EXPLAIN API...")
    try:
        response = requests.post(EXPLAIN_URL, json={"features": sample}, timeout=10)
        if response.status_code == 200:
            res = response.json()
            print("\n[SUCCESS] Explanation received.")
            print(f"   - Base Value: {res['base_value']:.4f}")
            print("   - Top 5 Contributors:")
            for i, item in enumerate(res["contributions"][:5], 1):
                # Simple ASCII bar chart for impact
                impact = item["shap_value"]
                bar = "+" * int(impact * 5) if impact > 0 else "-" * int(abs(impact) * 5)
                # Split long f-string for linter compliance
                print(
                    f"     {i}. {item['feature']:<20} | "
                    f"Val: {item['value']:>8.2f} | "
                    f"SHAP: {impact:>6.3f} {bar}"
                )
        else:
            print(f"\n[FAIL] API Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"\n[FAIL] Request failed: {e}")


if __name__ == "__main__":
    print("========================================")
    print("NIDS API Live Integration Test")
    print("========================================")

    # 1. Get Samples
    malicious_sample = get_random_sample("infogathering.csv")
    benign_sample = get_random_sample("benign_web_https.csv")

    # 2. Test Predictions
    print("\n--- TEST 1: Predictions ---")
    test_prediction(malicious_sample, "MALICIOUS")
    test_prediction(benign_sample, "BENIGN")

    # 3. Test Explanations
    print("\n--- TEST 2: Explanations (SHAP) ---")
    test_explanation(malicious_sample, "MALICIOUS")
    test_explanation(benign_sample, "BENIGN")

    print("\n========================================")

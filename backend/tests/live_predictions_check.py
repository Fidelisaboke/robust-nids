import os

import pandas as pd
import requests

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/v1/nids/predict/full"

# Define paths using separate steps to keep line lengths manageable for linters
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


def test_endpoint(sample, expected_type):
    """Sends the sample to the API and validates the response."""
    if sample is None:
        return

    print(f"\n-> Sending {expected_type} sample to API...")

    try:
        response = requests.post(API_URL, json={"features": sample}, timeout=5)

        if response.status_code == 200:
            res = response.json()
            threat = res["threat_level"]
            bin_res = res["binary"]
            multi_res = res["multiclass"]
            anom_res = res["anomaly"]

            print("\n[SUCCESS] API response received.")
            print(f"   - Threat Level: [{threat}]")
            print(f"   - Binary:       {bin_res['label']} ({bin_res['confidence']:.4f})")
            print(f"   - Multiclass:   {multi_res['label']} ({multi_res['confidence']:.4f})")
            print(
                f"   - Anomaly Score: {anom_res['anomaly_score']:.4f} "
                f"(Threshold: {anom_res['threshold']:.4f})"
            )

            # Validation logic
            is_malicious = expected_type == "MALICIOUS"
            threat_high = threat in ["High", "Critical"]
            threat_low = threat in ["Low", "Medium"]

            if (is_malicious and threat_high) or (not is_malicious and threat_low):
                print(">> VERDICT: PASS")
            else:
                print(f">> VERDICT: SUSPICIOUS (Expected {expected_type}, got {threat})")

        else:
            print(f"\n[FAIL] API Error ({response.status_code})")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("\n[FAIL] Connection failed. Is 'uvicorn main:app' running?")


if __name__ == "__main__":
    print("========================================")
    print("NIDS API Live Integration Test")
    print("========================================")

    print("\n--- TEST CASE 1: Known Attack (Port Scan) ---")
    test_endpoint(get_random_sample("infogathering.csv"), "MALICIOUS")

    print("\n--- TEST CASE 2: Known Benign (Web) ---")
    test_endpoint(get_random_sample("benign_web_https.csv"), "BENIGN")

    print("\n========================================")

import glob
import json
import os
import subprocess
import time

import pandas as pd
import requests

from utils.constants import BENIGN_LABELS

# --- Configuration ---
CAPTURE_DIR = "/tmp/nids_live"
API_URL = "http://127.0.0.1:8000/api/v1/nids/predict/full"
SLEEP_INTERVAL = 2

# Log file for interesting flows (copy-paste these into your dashboard)
DEBUG_LOG = "/tmp/nids_debug_flows.jsonl"

# Ignore benign traffic labels in console output (reduced noise)
IGNORED_LABELS = BENIGN_LABELS

# Ports used in demo scripts that should not be suppressed
DEMO_TARGET_PORTS = [8085, 8081, 8082, 2222, 9999, 9998]

# Ensure capture directory exists
os.makedirs(CAPTURE_DIR, exist_ok=True)

print("========================================")
print("  NIDS Live Processor Agent Active")
print("========================================")
print(f"Interesting flows will be saved to: {DEBUG_LOG}")
print("Artifacts will be deleted after processing.")


def is_benign_noise(row):
    """
    Suppresses environment-specific benign flows that often cause false positives.
    """
    src_ip = row.get("src_ip")
    dst_ip = row.get("dst_ip")
    try:
        src_port = int(row.get("src_port", 0))
        dst_port = int(row.get("dst_port", 0))
    except (ValueError, TypeError):
        # Invalid port values are likely malformed packets or noise
        return True

    if dst_port in DEMO_TARGET_PORTS:
        return False

    # 1. WSL2 DNS internal chatter
    if dst_port == 53 and (src_ip == "10.255.255.254" or dst_ip == "10.255.255.254"):
        return True
    # 2. Local multicast
    if (dst_ip == "224.0.0.251" and dst_port == 5353) or (dst_ip == "239.255.255.250" and dst_port == 1900):
        return True
    # 3. Backend API loopback
    if dst_port == 8000 and src_ip == "127.0.0.1" and dst_ip == "127.0.0.1":
        return True
    # 4a/b. Standard HTTP/HTTPS noise
    if src_port in [80, 443] and dst_port > 1024:
        return True
    if dst_port in [80, 443] and src_port > 1024:
        return True
    # 5. Localhost IPC
    if src_ip == "127.0.0.1" and dst_ip == "127.0.0.1" and src_port > 1024 and dst_port > 1024:
        return True
    # 6. NTP
    if dst_port == 123 or src_port == 123:
        return True

    return False


def is_valid_pcap(pcap_path):
    if os.path.getsize(pcap_path) <= 24:
        return False
    return True


def run_feature_extraction(pcap_path, csv_path):
    try:
        cmd = ["cicflowmeter", "-f", pcap_path, "-c", csv_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False
        return True
    except Exception as e:
        print(f" [!] Exception in run_feature_extraction: {e}")
        return False


def save_debug_json(row, info_str):
    """Appends the flow row as JSON to the debug log."""
    try:
        data = row.to_dict()
        # Add metadata so you know why it was saved (remove before pasting to dashboard)
        # data["_DEBUG_INFO"] = info_str
        with open(DEBUG_LOG, "a") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print(f" [!] Failed to save debug JSON: {e}")


def process_flow_row(row, is_first_alert):
    """
    Processes a single flow row with targeted debugging and JSON logging.
    """
    try:
        dst_port = int(row.get("dst_port", 0))
        is_debug_target = dst_port in DEMO_TARGET_PORTS
    except (ValueError, TypeError) as e:
        print(f" [!] Exception in process_flow_row (port parsing): {e}")
        is_debug_target = False

    if not is_debug_target and is_benign_noise(row):
        return False

    try:
        response = requests.post(API_URL, json={"features": row.to_dict()}, timeout=5)
        if response.status_code == 200:
            res = response.json()

            # Alert Condition: High Threat OR Debug Target
            if res["threat_level"] in ["High", "Critical"] or is_debug_target:
                atk_type = res["multiclass"]["label"]
                threat = res["threat_level"]
                conf = res["binary"]["confidence"]

                # Console Output
                if atk_type not in IGNORED_LABELS or is_debug_target:
                    if is_first_alert:
                        print("\n", end="")
                    src = f"{row.get('src_ip')}:{row.get('src_port')}"
                    dst = f"{row.get('dst_ip')}:{row.get('dst_port')}"
                    icon = (
                        "🔍 DEBUG" if (is_debug_target and threat not in ["High", "Critical"]) else "🚨 ALERT"
                    )
                    print(f"   {icon}: {src} -> {dst} | {atk_type} [{threat}] (Conf: {conf:.2f})")

                    # SAVE JSON FOR ANALYSIS
                    save_debug_json(row, f"{icon}: {atk_type} [{threat}]")
                    return True
    except Exception as e:
        print(f" [!] Exception in process_flow_row: {e}")
    return False


def transmit_flows(csv_path):
    if not os.path.exists(csv_path):
        return
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return
        print(f" [v] Scanned {len(df)} flows...", end="", flush=True)
        alerts = 0
        for _, row in df.iterrows():
            if process_flow_row(row, is_first_alert=(alerts == 0)):
                alerts += 1
        if alerts == 0:
            print(" OK.")
        else:
            print(f"   [!] Found {alerts} suspicious flows (saved to {DEBUG_LOG}).")
    except Exception as e:
        print(f" [!] Exception in transmit_flows: {e}")


def cleanup_files(pcap_path, csv_path):
    try:
        if os.path.exists(pcap_path):
            os.remove(pcap_path)
        if os.path.exists(csv_path):
            os.remove(csv_path)
    except Exception as e:
        print(f" [!] Exception in cleanup_files: {e}")


def process_pcap(pcap_path):
    csv_path = pcap_path.replace(".pcap", ".csv")
    if not is_valid_pcap(pcap_path):
        os.remove(pcap_path)
        return
    try:
        if run_feature_extraction(pcap_path, csv_path):
            transmit_flows(csv_path)
    finally:
        cleanup_files(pcap_path, csv_path)


def main_loop():
    print(f"Watching: {CAPTURE_DIR}...")
    # Clear previous debug log on start
    if os.path.exists(DEBUG_LOG):
        os.remove(DEBUG_LOG)

    while True:
        pcaps = sorted(glob.glob(os.path.join(CAPTURE_DIR, "*.pcap")))
        if len(pcaps) > 1:
            for pcap in pcaps[:-1]:
                process_pcap(pcap)
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nStopping.")

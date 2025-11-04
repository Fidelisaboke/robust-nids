#!/usr/bin/env python3
import argparse

import numpy as np
import pandas as pd
from scapy.all import IP, TCP, UDP, PcapReader

# Top 20 features for binary and multiclass
FEATURES = {
    "binary": [
        "Total Fwd Packet",
        "Flow Duration",
        "Packet Length Min",
        "Bwd Bytes/Bulk Avg",
        "Average Packet Size",
        "Bwd IAT Mean",
        "Flow IAT Min",
        "SYN Flag Count",
        "Fwd Act Data Pkts",
        "Protocol_6.0",
        "Bwd Packet Length Std",
        "Total Length of Bwd Packet",
        "Bwd Init Win Bytes",
        "Total Bwd packets",
        "FWD Init Win Bytes",
        "Subflow Fwd Packets",
        "Bwd Packet Length Max",
        "Fwd Seg Size Min",
        "Subflow Fwd Bytes",
        "RST Flag Count",
    ],
    "multiclass": [
        "Average Packet Size",
        "Total Length of Bwd Packet",
        "Packet Length Min",
        "Flow Bytes/s",
        "FWD Init Win Bytes",
        "Bwd Packet Length Mean",
        "Protocol_6.0",
        "Total Bwd packets",
        "Bwd Packet Length Min",
        "Bwd Bytes/Bulk Avg",
        "Fwd Seg Size Min",
        "Subflow Fwd Bytes",
        "Bwd Bulk Rate Avg",
        "SYN Flag Count",
        "Bwd Packet Length Max",
        "Flow IAT Mean",
        "Flow IAT Min",
        "FIN Flag Count",
        "Bwd IAT Total",
        "Fwd Act Data Pkts",
    ],
}

# Filtering thresholds
MIN_FWD_PKTS = 1
MIN_BWD_PKTS = 1
MIN_FLOW_DURATION = 1e-6
MIN_DURATION_FOR_RATE = 1e-6

# CRITICAL: Flow timeout settings to match standard flow exporters
FLOW_INACTIVE_TIMEOUT = 15.0  # seconds - end flow after 15s of inactivity
FLOW_ACTIVE_TIMEOUT = 120.0  # seconds - split flows longer than 120s


def _pkt_payload_len(pkt):
    """Return payload length (int) for TCP/UDP packets, 0 otherwise."""
    try:
        if TCP in pkt:
            return len(bytes(pkt[TCP].payload))
        if UDP in pkt:
            return len(bytes(pkt[UDP].payload))
    except Exception:
        return 0
    return 0


def _count_tcp_flags(pkt):
    syn_count, rst_count, fin_count = 0, 0, 0
    if TCP in pkt:
        flags = int(pkt[TCP].flags)
        if flags & 0x02:
            syn_count += 1
        if flags & 0x04:
            rst_count += 1
        if flags & 0x01:
            fin_count += 1
    return syn_count, rst_count, fin_count


def _get_init_win(pkt):
    try:
        if pkt is not None and TCP in pkt:
            return int(pkt[TCP].window)
    except Exception:
        pass
    return 0


def _extract_packet_info(pkt):
    """Extract flow key and packet data from a Scapy packet, or return None if not valid."""
    if IP not in pkt:
        return None, None
    proto = int(pkt[IP].proto)
    if proto not in (6, 17):
        return None, None

    src = pkt[IP].src
    dst = pkt[IP].dst

    if TCP in pkt:
        sport = int(pkt[TCP].sport)
        dport = int(pkt[TCP].dport)
    elif UDP in pkt:
        sport = int(pkt[UDP].sport)
        dport = int(pkt[UDP].dport)
    else:
        sport, dport = 0, 0

    # Create a canonical flow key (sorted)
    if src < dst:
        key = (src, dst, proto, sport, dport)
    elif dst < src:
        key = (dst, src, proto, dport, sport)
    else:  # Handle loopback (src == dst)
        if sport < dport:
            key = (src, dst, proto, sport, dport)
        else:
            key = (src, dst, proto, dport, sport)

    time = float(pkt.time)
    pkt_len = len(pkt)
    payload_len = _pkt_payload_len(pkt)
    flags = _count_tcp_flags(pkt)  # (syn, rst, fin)
    init_win = _get_init_win(pkt)

    pkt_data = (time, pkt_len, payload_len, src, sport, flags, init_win)
    return key, pkt_data


def process_pcap_with_timeouts(pcap_file):
    """
    Build flows with proper timeout handling.
    Flows are expired based on:
    1. Inactive timeout: No packets for FLOW_INACTIVE_TIMEOUT seconds
    2. Active timeout: Flow duration exceeds FLOW_ACTIVE_TIMEOUT seconds
    """
    active_flows = {}  # key -> (packet_list, last_packet_time, flow_start_time)
    completed_flows = []

    print(f"Starting PCAP stream processing with timeouts for: {pcap_file}")
    print(f"  Inactive timeout: {FLOW_INACTIVE_TIMEOUT}s")
    print(f"  Active timeout: {FLOW_ACTIVE_TIMEOUT}s")

    packet_count = 0
    with PcapReader(pcap_file) as pcap_reader:
        for pkt in pcap_reader:
            packet_count += 1
            if packet_count % 20000 == 0:
                print(f"  ... processed {packet_count} packets, {len(completed_flows)} flows completed ...")

            try:
                key, pkt_data = _extract_packet_info(pkt)
                if key is None or pkt_data is None:
                    continue

                pkt_time = pkt_data[0]

                # Check if flow exists
                if key in active_flows:
                    packet_list, last_time, start_time = active_flows[key]

                    # Check for inactive timeout
                    if (pkt_time - last_time) > FLOW_INACTIVE_TIMEOUT:
                        # Flow expired due to inactivity - save it
                        completed_flows.append((key, packet_list))
                        active_flows[key] = ([pkt_data], pkt_time, pkt_time)
                    # Check for active timeout
                    elif (pkt_time - start_time) > FLOW_ACTIVE_TIMEOUT:
                        # Flow expired due to duration - save it
                        completed_flows.append((key, packet_list))
                        active_flows[key] = ([pkt_data], pkt_time, pkt_time)
                    else:
                        # Continue existing flow
                        packet_list.append(pkt_data)
                        active_flows[key] = (packet_list, pkt_time, start_time)
                else:
                    # New flow
                    active_flows[key] = ([pkt_data], pkt_time, pkt_time)

            except Exception as e:
                print(f"Warning: Skipping corrupt packet {packet_count}: {e}")
                pass

    # Add remaining active flows
    for key, (packet_list, _, _) in active_flows.items():
        completed_flows.append((key, packet_list))

    print(f"PCAP stream complete. Processed {packet_count} packets into {len(completed_flows)} flows.")
    return completed_flows


def _extract_flow_stats(flow_key, packet_data_list):
    """Extract statistics from a list of lightweight packet data tuples."""
    timestamps = []
    fwd_timestamps = []
    bwd_timestamps = []

    fwd_lengths = []
    bwd_lengths = []
    pkt_lengths = []
    fwd_payload_count = 0
    syn_count, rst_count, fin_count = 0, 0, 0
    subflow_fwd_packets = 0
    fwd_init_win = 0
    bwd_init_win = 0
    first_fwd_set = False
    first_bwd_set = False
    fwd_len, bwd_len = 0, 0

    flow_src_ip = flow_key[0]
    flow_src_port = flow_key[3]

    for pkt_data in packet_data_list:
        time, pkt_len, payload_len, pkt_src_ip, pkt_src_port, flags, init_win = pkt_data

        timestamps.append(time)
        pkt_lengths.append(pkt_len)

        s, r, f = flags
        syn_count += s
        rst_count += r
        fin_count += f

        if pkt_src_ip == flow_src_ip and pkt_src_port == flow_src_port:
            # Forward packet
            fwd_timestamps.append(time)
            fwd_lengths.append(pkt_len)
            fwd_len += pkt_len
            if payload_len > 0:
                fwd_payload_count += 1
            if s > 0:
                subflow_fwd_packets += 1
            if not first_fwd_set:
                fwd_init_win = init_win
                first_fwd_set = True
        else:
            # Backward packet
            bwd_timestamps.append(time)
            bwd_lengths.append(pkt_len)
            bwd_len += pkt_len
            if not first_bwd_set:
                bwd_init_win = init_win
                first_bwd_set = True

    flow_duration = max(timestamps) - min(timestamps) if timestamps else 0.0

    return {
        "timestamps": timestamps,
        "fwd_timestamps": fwd_timestamps,
        "bwd_timestamps": bwd_timestamps,
        "flow_duration": flow_duration,
        "fwd_lengths": fwd_lengths,
        "bwd_lengths": bwd_lengths,
        "pkt_lengths": pkt_lengths,
        "fwd_payload_count": fwd_payload_count,
        "syn_count": syn_count,
        "rst_count": rst_count,
        "fin_count": fin_count,
        "subflow_fwd_packets": subflow_fwd_packets,
        "fwd_init_win": fwd_init_win,
        "bwd_init_win": bwd_init_win,
        "fwd_len": fwd_len,
        "bwd_len": bwd_len,
    }


def _compute_feature_row(flow_key, stats, mode):
    """Compute a feature row from flow statistics."""
    timestamps = np.array(stats["timestamps"], dtype=float)
    fwd_timestamps = np.array(stats["fwd_timestamps"], dtype=float)
    bwd_timestamps = np.array(stats["bwd_timestamps"], dtype=float)

    timestamps.sort()
    fwd_timestamps.sort()
    bwd_timestamps.sort()

    flow_duration = stats["flow_duration"]
    fwd_lengths = stats["fwd_lengths"]
    bwd_lengths = stats["bwd_lengths"]
    pkt_lengths = stats["pkt_lengths"]
    fwd_payload_count = stats["fwd_payload_count"]
    syn_count = stats["syn_count"]
    rst_count = stats["rst_count"]
    fin_count = stats["fin_count"]
    subflow_fwd_packets = stats["subflow_fwd_packets"]
    fwd_init_win = stats["fwd_init_win"]
    bwd_init_win = stats["bwd_init_win"]
    fwd_len = stats["fwd_len"]
    bwd_len = stats["bwd_len"]

    fwd_pkt_count = len(fwd_lengths)
    bwd_pkt_count = len(bwd_lengths)

    # Remove flows that do not meet minimum criteria
    if fwd_pkt_count < MIN_FWD_PKTS or bwd_pkt_count < MIN_BWD_PKTS:
        return None
    if flow_duration < MIN_FLOW_DURATION:
        return None

    # Inter-Arrival Time (IAT)
    iat = np.diff(timestamps) if len(timestamps) > 1 else np.array([0.0])
    bwd_iat = np.diff(bwd_timestamps) if len(bwd_timestamps) > 1 else np.array([0.0])

    # Compute packet statistics
    avg_pkt_size = float(np.mean(pkt_lengths)) if pkt_lengths else 0.0
    bwd_pkt_std = float(np.std(bwd_lengths)) if bwd_lengths else 0.0
    bwd_pkt_max = int(max(bwd_lengths)) if bwd_lengths else 0
    bwd_pkt_min = int(min(bwd_lengths)) if bwd_lengths else 0
    bwd_pkt_mean = float(np.mean(bwd_lengths)) if bwd_lengths else 0.0
    total_fwd_bytes = int(fwd_len)
    total_bwd_bytes = int(bwd_len)

    duration_for_rate = max(flow_duration, MIN_DURATION_FOR_RATE)
    flow_bytes_per_s = (total_fwd_bytes + total_bwd_bytes) / duration_for_rate
    bwd_bulk_rate = total_bwd_bytes / duration_for_rate if duration_for_rate > 0 else 0.0
    bwd_bytes_bulk_avg = total_bwd_bytes / bwd_pkt_count if bwd_pkt_count else 0.0
    fwd_seg_size_min = int(min(fwd_lengths)) if fwd_lengths else 0

    feature_map = {
        "Total Fwd Packet": fwd_pkt_count,
        "Total Bwd packets": bwd_pkt_count,
        "Flow Duration": float(flow_duration),
        "Packet Length Min": int(min(pkt_lengths)) if pkt_lengths else 0,
        "Average Packet Size": float(avg_pkt_size),
        "Flow IAT Min": float(np.min(iat)) if iat.size else 0.0,
        "Flow IAT Mean": float(np.mean(iat)) if iat.size else 0.0,
        "Bwd IAT Mean": float(np.mean(bwd_iat)) if bwd_iat.size else 0.0,
        "Bwd IAT Total": float(np.sum(bwd_iat)) if bwd_iat.size else 0.0,
        "SYN Flag Count": syn_count,
        "RST Flag Count": rst_count,
        "FIN Flag Count": fin_count,
        "FWD Init Win Bytes": int(fwd_init_win),
        "Bwd Init Win Bytes": int(bwd_init_win),
        "Protocol_6.0": 1 if int(flow_key[2]) == 6 else 0,
        "Fwd Act Data Pkts": fwd_payload_count,
        "Subflow Fwd Packets": subflow_fwd_packets,
        "Subflow Fwd Bytes": total_fwd_bytes,
        "Total Length of Bwd Packet": total_bwd_bytes,
        "Bwd Packet Length Std": float(bwd_pkt_std),
        "Bwd Packet Length Max": bwd_pkt_max,
        "Bwd Packet Length Mean": float(bwd_pkt_mean),
        "Bwd Packet Length Min": bwd_pkt_min,
        "Bwd Bytes/Bulk Avg": float(bwd_bytes_bulk_avg),
        "Fwd Seg Size Min": fwd_seg_size_min,
        "Flow Bytes/s": float(flow_bytes_per_s),
        "Bwd Bulk Rate Avg": float(bwd_bulk_rate),
    }

    return [feature_map.get(f, 0.0) for f in FEATURES[mode]]


def compute_features(flows, mode="binary"):
    """Compute features per flow using the FEATURES[mode] ordering."""
    print(f"Computing features for {len(flows)} flows...")
    data = []
    flow_count = len(flows)

    saved_count = 0
    for i, (flow_key, packets) in enumerate(flows):
        if (i + 1) % 5000 == 0:
            print(f"  ... computed features for {i + 1}/{flow_count} flows ...")

        if not packets:
            continue

        stats = _extract_flow_stats(flow_key, packets)
        row = _compute_feature_row(flow_key, stats, mode)

        if row is not None:
            data.append(row)
            saved_count += 1

    print(f"Feature computation complete. {saved_count} flows passed filters.")
    df = pd.DataFrame(data, columns=FEATURES[mode])
    return df


def main(pcap_file, output_csv, mode):
    flows = process_pcap_with_timeouts(pcap_file)
    df = compute_features(flows, mode)

    # Print statistics for debugging
    print("\n=== Flow Statistics ===")
    print(f"Total flows: {len(df)}")
    if len(df) > 0:
        print("\nAverage Packet Size stats:")
        print(f"  Mean: {df['Average Packet Size'].mean():.2f}")
        print(f"  Min: {df['Average Packet Size'].min():.2f}")
        print(f"  Max: {df['Average Packet Size'].max():.2f}")

    df.to_csv(output_csv, index=False)
    print(f"\nSaved {len(df)} flows to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", required=True, help="Input PCAP file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    parser.add_argument("--mode", choices=["binary", "multiclass"], default="binary", help="Feature set mode")
    args = parser.parse_args()

    main(args.pcap, args.output, args.mode)

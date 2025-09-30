"""
Analytics Page - Deep dive analytics and visualizations
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def show():
    """Render the analytics page"""

    st.header("📈 Advanced Analytics")

    # Time range selector
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        time_range = st.selectbox("Time Range", ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"], index=1)

    with col2:
        analysis_type = st.selectbox(
            "Analysis Type", ["Traffic Patterns", "Threat Intelligence", "Model Performance", "Network Topology"]
        )

    with col3:
        st.markdown("")  # Spacer

    st.markdown("---")

    if analysis_type == "Traffic Patterns":
        show_traffic_patterns(time_range)
    elif analysis_type == "Threat Intelligence":
        show_threat_intelligence(time_range)
    elif analysis_type == "Model Performance":
        show_model_performance(time_range)
    elif analysis_type == "Network Topology":
        show_network_topology(time_range)


def show_traffic_patterns(time_range):
    """Show traffic pattern analysis"""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Traffic Volume Heatmap")

        # Generate sample heatmap data
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = [f"{i:02d}:00" for i in range(24)]

        # Create sample traffic volume data
        traffic_matrix = np.random.randint(100, 1000, size=(7, 24))

        fig = px.imshow(
            traffic_matrix,
            x=hours,
            y=days,
            aspect="auto",
            color_continuous_scale="Blues",
            title="Network Traffic Volume by Day and Hour",
        )
        fig.update_xaxes(side="bottom")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Protocol Distribution")

        protocols = ["HTTP/HTTPS", "TCP", "UDP", "ICMP", "DNS", "SSH", "FTP", "Other"]
        percentages = [35, 25, 15, 8, 7, 5, 3, 2]

        fig = go.Figure(data=[go.Bar(x=protocols, y=percentages)])
        fig.update_layout(
            title="Network Protocol Usage (%)", xaxis_title="Protocol", yaxis_title="Percentage", showlegend=False
        )
        st.plotly_chart(fig, width="stretch")

    # Detailed traffic statistics
    st.subheader("Traffic Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Peak Traffic", "15.2K pps", "12% ↑")
    with col2:
        st.metric("Avg Packet Size", "1,247 bytes", "3% ↓")
    with col3:
        st.metric("Unique IPs", "2,847", "156 ↑")
    with col4:
        st.metric("Bandwidth Usage", "85.3%", "8% ↑")


def show_threat_intelligence(time_range):
    """Show threat intelligence analysis"""

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Threat Trends Over Time")

        # Generate sample threat trend data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq="D")

        threat_data = pd.DataFrame(
            {
                "date": dates,
                "ddos": np.random.poisson(5, len(dates)),
                "malware": np.random.poisson(3, len(dates)),
                "intrusion": np.random.poisson(2, len(dates)),
                "scanning": np.random.poisson(8, len(dates)),
            }
        )

        fig = go.Figure()
        for col in ["ddos", "malware", "intrusion", "scanning"]:
            fig.add_trace(
                go.Scatter(
                    x=threat_data["date"], y=threat_data[col], mode="lines+markers", name=col.upper(), stackgroup="one"
                )
            )

        fig.update_layout(
            title="Threat Detection Trends (Last 30 Days)",
            xaxis_title="Date",
            yaxis_title="Number of Threats",
            hovermode="x unified",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Top Attack Sources")

        # Sample attack source data
        attack_sources = pd.DataFrame(
            {
                "IP": ["192.168.1.100", "10.0.0.45", "172.16.0.23", "203.0.113.1", "198.51.100.1"],
                "Country": ["Unknown", "US", "CN", "RU", "KP"],
                "Attacks": [45, 32, 28, 21, 18],
                "Type": ["DDoS", "Scan", "Malware", "Brute Force", "Injection"],
            }
        )

        for idx, row in attack_sources.iterrows():
            with st.container():
                st.markdown(
                    f"""
                **{row['IP']}** ({row['Country']})
                {row['Attacks']} attacks - {row['Type']}
                """
                )
                st.progress(row["Attacks"] / 50)

    st.markdown("---")

    # Attack pattern analysis
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Attack Severity Distribution")

        severity_data = ["Critical", "High", "Medium", "Low"]
        severity_counts = [12, 28, 45, 23]
        colors = ["#dc3545", "#fd7e14", "#ffc107", "#28a745"]

        fig = px.pie(
            names=severity_data,
            values=severity_counts,
            color_discrete_sequence=colors,
            title="Attack Severity Distribution",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Attack Success Rate")

        attack_types = ["DDoS", "Malware", "Injection", "Brute Force", "Scanning"]
        success_rates = [15, 8, 25, 35, 45]

        fig = go.Figure(data=[go.Bar(x=attack_types, y=success_rates, marker=dict(color="rgba(255, 99, 132, 0.6)"))])
        fig.update_layout(
            title="Attack Success Rate by Type (%)", xaxis_title="Attack Type", yaxis_title="Success Rate (%)"
        )
        st.plotly_chart(fig, width="stretch")


def show_model_performance(time_range):
    """Show model performance analytics"""

    st.subheader("Model Performance Metrics")

    # Performance metrics over time
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Accuracy Trends")

        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq="D")
        performance_data = pd.DataFrame(
            {
                "date": dates,
                "accuracy": 0.95 + np.random.normal(0, 0.01, len(dates)),
                "precision": 0.94 + np.random.normal(0, 0.015, len(dates)),
                "recall": 0.96 + np.random.normal(0, 0.012, len(dates)),
                "f1_score": 0.95 + np.random.normal(0, 0.008, len(dates)),
            }
        )

        fig = go.Figure()
        for metric in ["accuracy", "precision", "recall", "f1_score"]:
            fig.add_trace(
                go.Scatter(
                    x=performance_data["date"],
                    y=performance_data[metric],
                    mode="lines",
                    name=metric.replace("_", " ").title(),
                )
            )

        fig.update_layout(
            title="Model Performance Over Time", xaxis_title="Date", yaxis_title="Score", yaxis=dict(range=[0.85, 1.0])
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Confusion Matrix")

        # Sample confusion matrix
        conf_matrix = np.array([[950, 25, 15, 10], [20, 945, 20, 15], [10, 15, 960, 15], [5, 10, 8, 977]])

        labels = ["Normal", "DDoS", "Intrusion", "Malware"]

        fig = px.imshow(conf_matrix, x=labels, y=labels, aspect="auto", color_continuous_scale="Blues", text_auto=True)
        fig.update_layout(title="Confusion Matrix - Current Model")
        st.plotly_chart(fig, width="stretch")

    # Feature importance
    st.subheader("Feature Importance Analysis")

    features = [
        "Packet Size",
        "Duration",
        "Protocol Type",
        "Source Port",
        "Dest Port",
        "Flow Rate",
        "Packet Count",
        "Byte Count",
        "TCP Flags",
        "IP Flags",
    ]
    importance = [0.15, 0.12, 0.11, 0.10, 0.09, 0.08, 0.08, 0.07, 0.06, 0.05]

    fig = go.Figure(data=[go.Bar(y=features, x=importance, orientation="h")])
    fig.update_layout(title="Top 10 Most Important Features", xaxis_title="Importance Score", yaxis_title="Features")
    st.plotly_chart(fig, width="stretch")


def show_network_topology(time_range):
    """Show network topology analysis"""

    st.subheader("Network Topology Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Network Flow Visualization")
        st.info(
            "Network topology visualization would be implemented here using libraries like "
            "NetworkX and Plotly for interactive network graphs."
        )

        # Placeholder for network topology
        st.markdown(
            """
        **Network Segments Analyzed:**
        - Internal Network: 192.168.1.0/24 (245 hosts)
        - DMZ: 10.0.1.0/24 (12 hosts)
        - Guest Network: 172.16.0.0/24 (89 hosts)
        - Server Farm: 10.0.2.0/24 (28 hosts)
        """
        )

    with col2:
        st.subheader("Network Statistics")

        st.metric("Active Hosts", "374", "12 ↑")
        st.metric("Network Segments", "4", "0")
        st.metric("Critical Assets", "28", "0")
        st.metric("Monitored Ports", "156", "3 ↑")

        st.subheader("Top Talkers")
        talkers_data = pd.DataFrame(
            {
                "Host": ["10.0.2.15", "192.168.1.100", "10.0.1.5", "172.16.0.23"],
                "Traffic (GB)": [15.2, 12.8, 8.9, 6.7],
                "Connections": [1250, 890, 567, 445],
            }
        )
        st.dataframe(talkers_data, width="stretch")


if __name__ == "__main__":
    show()

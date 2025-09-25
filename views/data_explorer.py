"""
Data Explorer Page - Network traffic data analysis and exploration
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def show():
    """Render the data explorer page"""

    st.header("🔍 Network Traffic Data Explorer")

    # Data source selection and filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Data source
        st.selectbox("Data Source", ["Live Traffic", "Historical Data", "Test Dataset", "Synthetic Data"])

    with col2:
        time_range = st.selectbox("Time Range", ["Last Hour", "Last 24 Hours", "Last 7 Days", "Custom Range"])

    with col3:
        # Protocol filter
        st.multiselect("Protocol", ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH", "FTP"], default=[])

    with col4:
        # Traffic type
        st.selectbox("Traffic Type", ["All Traffic", "Normal Only", "Suspicious Only", "Malicious Only"])

    if time_range == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            # Start date
            st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
        with col2:
            # End date
            st.date_input("End Date", datetime.now().date())

    st.markdown("---")

    # Data overview tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Feature Analysis", "Flow Analysis", "Raw Data"])

    with tab1:
        show_data_overview()

    with tab2:
        show_feature_analysis()

    with tab3:
        show_flow_analysis()

    with tab4:
        show_raw_data()


def show_data_overview():
    """Display data overview and statistics"""

    st.subheader("Dataset Overview")

    # Dataset statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", "2,456,789", "12,456 ↑")
    with col2:
        st.metric("Unique IPs", "8,234", "156 ↑")
    with col3:
        st.metric("Data Size", "15.7 GB", "234 MB ↑")
    with col4:
        st.metric("Features", "42", "0")

    st.markdown("---")

    # Traffic distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Traffic Classification Distribution")

        # Sample traffic distribution data
        traffic_labels = ["Normal", "DDoS", "Port Scan", "Brute Force", "Malware", "Other"]
        traffic_counts = [2100000, 156000, 89000, 67000, 34000, 10789]

        fig = px.pie(values=traffic_counts, names=traffic_labels, title="Traffic Type Distribution")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Protocol Distribution")

        protocol_data = pd.DataFrame(
            {
                "Protocol": ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH", "Other"],
                "Count": [1200000, 800000, 150000, 200000, 180000, 120000, 45000, 61789],
                "Percentage": [48.8, 32.5, 6.1, 8.1, 7.3, 4.9, 1.8, 2.5],
            }
        )

        fig = px.bar(protocol_data, x="Protocol", y="Count", title="Network Protocol Usage")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, width="stretch")

    # Data quality metrics
    st.subheader("Data Quality Assessment")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Missing Values")

        missing_data = pd.DataFrame(
            {
                "Feature": [
                    "src_ip",
                    "dst_ip",
                    "src_port",
                    "dst_port",
                    "protocol",
                    "packet_size",
                    "duration",
                    "flow_rate",
                    "tcp_flags",
                    "label",
                ],
                "Missing (%)": [0.0, 0.0, 0.1, 0.1, 0.0, 0.3, 0.5, 0.8, 2.1, 0.0],
            }
        )

        fig = px.bar(missing_data, x="Missing (%)", y="Feature", orientation="h", title="Missing Values by Feature")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Data Quality Score")

        quality_metrics = {"Completeness": 99.2, "Consistency": 98.7, "Accuracy": 99.5, "Timeliness": 98.9}

        for metric, score in quality_metrics.items():
            st.metric(metric, f"{score}%")
            # progress_color = "normal" if score >= 95 else "inverse"
            st.progress(score / 100)

    with col3:
        st.subheader("Data Freshness")

        st.metric("Last Update", "2 min ago")
        st.metric("Update Frequency", "Real-time")
        st.metric("Data Lag", "< 5 seconds")
        st.metric("Uptime", "99.97%")


def show_feature_analysis():
    """Display feature analysis and distributions"""

    st.subheader("Feature Analysis & Distributions")

    # Feature selection
    features = [
        "packet_size",
        "flow_duration",
        "flow_rate",
        "packet_count",
        "byte_count",
        "src_port",
        "dst_port",
        "tcp_flags",
        "protocol_type",
        "inter_arrival_time",
    ]

    selected_features = st.multiselect(
        "Select Features to Analyze", features, default=["packet_size", "flow_duration", "flow_rate"]
    )

    if selected_features:
        # Feature distributions
        col1, col2 = st.columns(2)

        for i, feature in enumerate(selected_features[:4]):  # Limit to 4 for display
            with col1 if i % 2 == 0 else col2:
                st.subheader(f"{feature.replace('_', ' ').title()} Distribution")

                # Generate sample distribution data
                if "size" in feature or "count" in feature:
                    data = np.random.lognormal(5, 1, 10000)
                elif "duration" in feature:
                    data = np.random.exponential(2, 10000)
                elif "rate" in feature:
                    data = np.random.gamma(2, 2, 10000)
                else:
                    data = np.random.normal(100, 20, 10000)

                fig = px.histogram(x=data, nbins=50, title=f"{feature.replace('_', ' ').title()} Distribution")
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, width="stretch")

    # Feature correlation analysis
    st.markdown("---")
    st.subheader("Feature Correlation Matrix")

    # Generate sample correlation matrix
    n_features = len(features)
    correlation_matrix = np.random.rand(n_features, n_features)
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2  # Make symmetric
    np.fill_diagonal(correlation_matrix, 1)  # Diagonal should be 1

    fig = px.imshow(
        correlation_matrix,
        x=features,
        y=features,
        color_continuous_scale="RdBu",
        aspect="auto",
        title="Feature Correlation Matrix",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

    # Feature statistics table
    st.subheader("Feature Statistics")

    stats_data = []
    for feature in features:
        # Generate sample statistics
        stats_data.append(
            {
                "Feature": feature,
                "Mean": np.random.uniform(10, 1000),
                "Std Dev": np.random.uniform(5, 200),
                "Min": np.random.uniform(0, 10),
                "Max": np.random.uniform(1000, 10000),
                "Skewness": np.random.uniform(-2, 5),
                "Kurtosis": np.random.uniform(-1, 10),
            }
        )

    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, width="stretch", hide_index=True)


def show_flow_analysis():
    """Display network flow analysis"""

    st.subheader("Network Flow Analysis")

    # Flow metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Active Flows", "12,456", "234 ↑")
    with col2:
        st.metric("Avg Flow Duration", "2.3s", "0.1s ↓")
    with col3:
        st.metric("Peak Flow Rate", "15.2K flows/sec", "1.2K ↑")
    with col4:
        st.metric("Long Flows (>60s)", "89", "12 ↓")

    st.markdown("---")

    # Flow analysis charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Flow Duration Distribution")

        # Generate sample flow duration data (log-normal distribution)
        flow_durations = np.random.lognormal(1, 2, 5000)
        flow_durations = flow_durations[flow_durations < 100]  # Limit for display

        fig = px.histogram(x=flow_durations, nbins=50, title="Network Flow Duration Distribution (seconds)")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Flow Size Distribution")

        # Generate sample flow size data
        flow_sizes = np.random.lognormal(8, 1.5, 5000) / 1000  # Convert to KB

        fig = px.histogram(x=flow_sizes, nbins=50, title="Network Flow Size Distribution (KB)")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    # Top flows analysis
    st.subheader("Top Network Flows")

    # Sample top flows data
    top_flows = pd.DataFrame(
        {
            "Flow ID": [f"FLW-{1000 + i:04d}" for i in range(10)],
            "Source IP": [f"192.168.1.{np.random.randint(1, 254)}" for _ in range(10)],
            "Dest IP": [f"10.0.0.{np.random.randint(1, 254)}" for _ in range(10)],
            "Protocol": np.random.choice(["TCP", "UDP", "HTTP", "HTTPS"], 10),
            "Duration (s)": np.random.uniform(0.1, 120, 10).round(2),
            "Packets": np.random.randint(10, 10000, 10),
            "Bytes": np.random.randint(1000, 1000000, 10),
            "Classification": np.random.choice(["Normal", "Suspicious", "Malicious"], 10, p=[0.8, 0.15, 0.05]),
        }
    )

    # Add color coding for classification
    def highlight_classification(val):
        if val == "Malicious":
            return "background-color: #f56565"
        elif val == "Suspicious":
            return "background-color: #ffeb3b"
        return ""

    styled_df = top_flows.style.map(highlight_classification, subset=["Classification"])
    st.dataframe(styled_df, width="stretch", hide_index=True)

    # Flow timeline
    st.subheader("Flow Activity Timeline")

    # Generate sample timeline data
    timeline_data = []
    for i in range(24):
        hour = datetime.now().replace(hour=i, minute=0, second=0, microsecond=0)
        timeline_data.append(
            {
                "Hour": hour,
                "Normal Flows": np.random.poisson(500),
                "Suspicious Flows": np.random.poisson(25),
                "Malicious Flows": np.random.poisson(5),
            }
        )

    timeline_df = pd.DataFrame(timeline_data)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timeline_df["Hour"],
            y=timeline_df["Normal Flows"],
            mode="lines+markers",
            name="Normal",
            line=dict(color="green"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=timeline_df["Hour"],
            y=timeline_df["Suspicious Flows"],
            mode="lines+markers",
            name="Suspicious",
            line=dict(color="orange"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=timeline_df["Hour"],
            y=timeline_df["Malicious Flows"],
            mode="lines+markers",
            name="Malicious",
            line=dict(color="red"),
        )
    )

    fig.update_layout(title="Network Flow Activity Over 24 Hours", xaxis_title="Time", yaxis_title="Number of Flows")
    st.plotly_chart(fig, width="stretch")


def show_raw_data():
    """Display raw network traffic data"""

    st.subheader("Raw Network Traffic Data")

    # Data filtering options
    col1, col2, col3 = st.columns(3)

    with col1:
        show_labels = st.checkbox("Show Classifications", value=True)
    with col2:
        sample_size = st.selectbox("Sample Size", [100, 500, 1000, 5000], index=1)
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    # Generate sample network traffic data
    sample_data = generate_sample_traffic_data(sample_size, include_labels=show_labels)

    # Search and filter functionality
    with st.expander("Search & Filter Options"):
        col1, col2, col3 = st.columns(3)

        with col1:
            ip_search = st.text_input("Search by IP Address")
        with col2:
            port_filter = st.number_input("Filter by Port", min_value=0, max_value=65535, value=0)
        with col3:
            protocol_search = st.selectbox("Filter by Protocol", ["All", "TCP", "UDP", "ICMP", "HTTP", "HTTPS"])

    # Apply filters
    filtered_data = sample_data.copy()

    if ip_search:
        filtered_data = filtered_data[
            filtered_data["src_ip"].str.contains(ip_search, case=False, na=False)
            | filtered_data["dst_ip"].str.contains(ip_search, case=False, na=False)
        ]

    if port_filter > 0:
        filtered_data = filtered_data[
            (filtered_data["src_port"] == port_filter) | (filtered_data["dst_port"] == port_filter)
        ]

    if protocol_search != "All":
        filtered_data = filtered_data[filtered_data["protocol"] == protocol_search]

    # Display data table
    st.subheader(f"Network Traffic Records ({len(filtered_data)} of {sample_size})")

    # Add row selection capability
    if not filtered_data.empty:
        # Selected rows
        st.dataframe(
            filtered_data,
            width="stretch",
            hide_index=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
                "packet_size": st.column_config.NumberColumn("Packet Size (bytes)", format="%d"),
                "duration": st.column_config.NumberColumn("Duration (s)", format="%.3f"),
            },
        )

        # Export options
        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"network_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        with col2:
            if st.button("📊 Generate Report"):
                st.info("Detailed analysis report generated - check Downloads folder")

        with col3:
            if st.button("🚨 Flag for Investigation"):
                st.success("Selected records flagged for manual investigation")
    else:
        st.warning("No records match the current filters.")

    # Data summary statistics
    if not filtered_data.empty:
        with st.expander("Data Summary Statistics"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Numerical Features Summary")
                numerical_cols = ["packet_size", "duration", "src_port", "dst_port"]
                if any(col in filtered_data.columns for col in numerical_cols):
                    available_numerical = [col for col in numerical_cols if col in filtered_data.columns]
                    st.dataframe(filtered_data[available_numerical].describe())

            with col2:
                st.subheader("Categorical Features Summary")
                categorical_cols = (
                    ["protocol", "classification"] if "classification" in filtered_data.columns else ["protocol"]
                )
                for col in categorical_cols:
                    if col in filtered_data.columns:
                        st.write(f"**{col.title()} Distribution:**")
                        st.write(filtered_data[col].value_counts().head(10))


def generate_sample_traffic_data(n_samples, include_labels=True):
    """Generate sample network traffic data"""

    protocols = ["TCP", "UDP", "HTTP", "HTTPS", "DNS", "SSH", "FTP", "ICMP"]
    classifications = ["Normal", "DDoS", "Port Scan", "Brute Force", "Malware", "Suspicious"]

    data = []
    for i in range(n_samples):
        record = {
            "timestamp": datetime.now() - timedelta(seconds=np.random.randint(0, 86400)),
            "src_ip": (
                f"{np.random.randint(1, 254)}."
                f"{np.random.randint(1, 254)}."
                f"{np.random.randint(1, 254)}."
                f"{np.random.randint(1, 254)}"
            ),
            "dst_ip": f"192.168.1.{np.random.randint(1, 254)}",
            "src_port": np.random.randint(1024, 65535),
            "dst_port": np.random.choice([80, 443, 22, 21, 25, 53, 3389, np.random.randint(1024, 65535)]),
            "protocol": np.random.choice(protocols),
            "packet_size": np.random.randint(64, 1500),
            "duration": np.random.exponential(2),
            "flow_rate": np.random.uniform(0.1, 1000),
            "packet_count": np.random.randint(1, 1000),
        }

        if include_labels:
            record["classification"] = np.random.choice(classifications, p=[0.85, 0.05, 0.04, 0.03, 0.02, 0.01])

        data.append(record)

    return pd.DataFrame(data)


if __name__ == "__main__":
    show()

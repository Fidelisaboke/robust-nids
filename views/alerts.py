"""
Alerts Page - Security alert management and investigation
"""

from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st


def show():
    """Render the alerts page"""

    st.header("🚨 Security Alerts Management")

    # Alert filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        severity_filter = st.multiselect(
            "Severity", ["Critical", "High", "Medium", "Low"], default=["Critical", "High"]
        )

    with col2:
        status_filter = st.multiselect(
            "Status", ["New", "Investigating", "Resolved", "False Positive"], default=["New", "Investigating"]
        )

    with col3:
        alert_type_filter = st.multiselect(
            "Alert Type", ["DDoS", "Malware", "Intrusion", "Port Scan", "Brute Force", "SQL Injection"], default=[]
        )

    with col4:
        # Time filter
        st.selectbox("Time Period", ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"], index=1)

    st.markdown("---")

    # Alert summary cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
        <div class="alert-card">
            <h3 style="color: #dc3545; margin: 0;">Critical Alerts</h3>
            <h2 style="margin: 0;">8</h2>
            <p style="color: #666; margin: 0;">Require immediate attention</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #fd7e14; margin: 0;">High Priority</h3>
            <h2 style="margin: 0;">15</h2>
            <p style="color: #666; margin: 0;">Investigate soon</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">Resolved Today</h3>
            <h2 style="margin: 0;">42</h2>
            <p style="color: #666; margin: 0;">Successfully mitigated</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
        <div class="metric-card">
            <h3 style="color: #6c757d; margin: 0;">False Positives</h3>
            <h2 style="margin: 0;">7</h2>
            <p style="color: #666; margin: 0;">Marked as benign</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Alert list and details
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Active Alerts")

        # Sample alerts data
        alerts_data = generate_sample_alerts()

        # Filter alerts based on selections
        filtered_alerts = filter_alerts(alerts_data, severity_filter, status_filter, alert_type_filter)

        # Display alerts table
        display_alerts_table(filtered_alerts)

    with col2:
        st.subheader("Alert Investigation")

        # Alert selection for investigation
        if not filtered_alerts.empty:
            selected_alert_id = st.selectbox(
                "Select Alert for Investigation", filtered_alerts["Alert ID"].tolist(), index=0
            )

            # Display selected alert details
            selected_alert = filtered_alerts[filtered_alerts["Alert ID"] == selected_alert_id].iloc[0]
            display_alert_details(selected_alert)
        else:
            st.info("No alerts match the current filters.")

    # Alert trends
    st.markdown("---")
    st.subheader("Alert Trends and Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Alerts by Severity (Last 7 Days)")

        # Sample data for alert trends
        dates = pd.date_range(start=datetime.now() - timedelta(days=6), end=datetime.now(), freq="D")
        trend_data = pd.DataFrame(
            {
                "Date": dates,
                "Critical": [2, 1, 3, 5, 2, 4, 3],
                "High": [8, 6, 9, 12, 7, 10, 8],
                "Medium": [15, 18, 14, 20, 16, 19, 17],
                "Low": [25, 22, 28, 30, 24, 27, 26],
            }
        )

        fig = px.line(trend_data, x="Date", y=["Critical", "High", "Medium", "Low"], title="Alert Trends by Severity")
        fig.update_layout(yaxis_title="Number of Alerts")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Response Time Statistics")

        response_data = pd.DataFrame(
            {
                "Severity": ["Critical", "High", "Medium", "Low"],
                "Avg Response Time (min)": [3.2, 12.5, 45.8, 120.3],
                "Target (min)": [5, 30, 60, 240],
            }
        )

        fig = px.bar(
            response_data,
            x="Severity",
            y=["Avg Response Time (min)", "Target (min)"],
            title="Average Response Time vs Target",
            barmode="group",
        )
        st.plotly_chart(fig, width="stretch")


def generate_sample_alerts():
    """Generate sample alert data"""

    alert_types = ["DDoS", "Malware", "Port Scan", "Brute Force", "SQL Injection", "Intrusion"]
    severities = ["Critical", "High", "Medium", "Low"]
    statuses = ["New", "Investigating", "Resolved", "False Positive"]

    import random

    alerts = []
    for i in range(50):
        alert = {
            "Alert ID": f"ALT-{2024000 + i:06d}",
            "Timestamp": datetime.now() - timedelta(hours=random.randint(0, 72)),
            "Type": random.choice(alert_types),
            "Severity": random.choice(severities),
            "Status": random.choice(statuses),
            "Source IP": (
                f"{random.randint(1, 254)}."
                f"{random.randint(1, 254)}."
                f"{random.randint(1, 254)}."
                f"{random.randint(1, 254)}"
            ),
            "Target IP": f"192.168.1.{random.randint(1, 254)}",
            "Description": f"Suspicious {random.choice(alert_types).lower()} activity detected",
            "Confidence": random.randint(75, 99),
            "Assigned To": random.choice(["Alice Smith", "Bob Jones", "Charlie Brown", "Unassigned"]),
        }
        alerts.append(alert)

    return pd.DataFrame(alerts)


def filter_alerts(alerts_df, severity_filter, status_filter, alert_type_filter):
    """Filter alerts based on user selections"""

    filtered = alerts_df.copy()

    if severity_filter:
        filtered = filtered[filtered["Severity"].isin(severity_filter)]

    if status_filter:
        filtered = filtered[filtered["Status"].isin(status_filter)]

    if alert_type_filter:
        filtered = filtered[filtered["Type"].isin(alert_type_filter)]

    return filtered.sort_values("Timestamp", ascending=False)


def display_alerts_table(alerts_df):
    """Display alerts in a formatted table"""

    if alerts_df.empty:
        st.info("No alerts match the current filters.")
        return

    # Format the dataframe for display
    display_df = alerts_df.copy()
    display_df["Timestamp"] = display_df["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

    # Add severity color coding
    def get_severity_emoji(severity):
        emoji_map = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}
        return emoji_map.get(severity, "⚪")

    display_df["Severity"] = display_df["Severity"].apply(lambda x: f"{get_severity_emoji(x)} {x}")

    # Select columns for display
    display_columns = ["Alert ID", "Timestamp", "Type", "Severity", "Status", "Source IP", "Confidence"]

    st.dataframe(
        display_df[display_columns],
        width="stretch",
        hide_index=True,
        column_config={
            "Confidence": st.column_config.ProgressColumn(
                "Confidence",
                help="Alert confidence score",
                min_value=0,
                max_value=100,
                format="%d%%",
            ),
        },
    )


def display_alert_details(alert):
    """Display detailed information for selected alert"""

    st.markdown("### Alert Details")

    # Alert header with severity styling
    severity_colors = {"Critical": "#dc3545", "High": "#fd7e14", "Medium": "#ffc107", "Low": "#28a745"}

    color = severity_colors.get(alert["Severity"], "#6c757d")

    st.markdown(
        f"""
    <div style="border-left: 4px solid {color};
                padding: 1rem; margin: 1rem 0;
                background-color: var(--background-color);
                color: var(--text-color);">
        <h4 style="margin: 0; color: {color};">{alert['Alert ID']}</h4>
        <p style="margin: 0.5rem 0 0 0;"><strong>{alert['Type']}</strong> - {alert['Severity']} Priority</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Alert information
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
        **Timestamp:** {alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
        **Status:** {alert['Status']}
        **Confidence:** {alert['Confidence']}%
        **Assigned To:** {alert['Assigned To']}
        """
        )

    with col2:
        st.markdown(
            f"""
        **Source IP:** {alert['Source IP']}
        **Target IP:** {alert['Target IP']}
        **Type:** {alert['Type']}
        **Description:** {alert['Description']}
        """
        )


if __name__ == "__main__":
    show()

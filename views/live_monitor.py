"""
Dashboard Page - Main overview of NIDS system
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def show():
    """Render the dashboard page"""

    st.header("📊 System Dashboard")

    # Real-time metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #1f77b4; margin: 0;">Total Traffic</h3>
            <h2 style="margin: 0;">2.4M</h2>
            <p style="color: #666; margin: 0;">Packets analyzed today</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ff6b6b; margin: 0;">Threats Detected</h3>
            <h2 style="margin: 0;">23</h2>
            <p style="color: #666; margin: 0;">High priority alerts</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">Model Accuracy</h3>
            <h2 style="margin: 0;">98.7%</h2>
            <p style="color: #666; margin: 0;">Current performance</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffc107; margin: 0;">False Positives</h3>
            <h2 style="margin: 0;">1.2%</h2>
            <p style="color: #666; margin: 0;">Last 24 hours</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Traffic Analysis (Last 24 Hours)")

        # Sample data for traffic over time
        times = pd.date_range(start=datetime.now() - timedelta(hours=24),
                              end=datetime.now(), freq='h')
        traffic_data = pd.DataFrame({
            'time': times,
            'normal_traffic': np.random.poisson(1000, len(times)),
            'suspicious_traffic': np.random.poisson(50, len(times)),
            'malicious_traffic': np.random.poisson(10, len(times))
        })

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=traffic_data['time'], y=traffic_data['normal_traffic'],
                                 mode='lines', name='Normal', line=dict(color='#28a745')))
        fig.add_trace(go.Scatter(x=traffic_data['time'], y=traffic_data['suspicious_traffic'],
                                 mode='lines', name='Suspicious', line=dict(color='#ffc107')))
        fig.add_trace(go.Scatter(x=traffic_data['time'], y=traffic_data['malicious_traffic'],
                                 mode='lines', name='Malicious', line=dict(color='#dc3545')))

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Packet Count",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Threat Distribution")

        # Sample threat distribution data
        threat_types = ['DDoS', 'Port Scan', 'SQL Injection', 'Malware', 'Brute Force', 'Other']
        threat_counts = [8, 5, 3, 4, 2, 1]

        fig = px.pie(values=threat_counts, names=threat_types,
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Recent alerts and system info
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🚨 Recent Alerts")

        # Sample recent alerts
        alerts_data = pd.DataFrame({
            'Timestamp': [
                datetime.now() - timedelta(minutes=5),
                datetime.now() - timedelta(minutes=12),
                datetime.now() - timedelta(minutes=18),
                datetime.now() - timedelta(minutes=25),
                datetime.now() - timedelta(minutes=32)
            ],
            'Type': ['DDoS Attack', 'Port Scan', 'SQL Injection', 'Brute Force', 'Malware Detection'],
            'Source IP': ['192.168.1.100', '10.0.0.45', '172.16.0.23', '192.168.1.200', '10.0.0.78'],
            'Severity': ['Critical', 'High', 'Medium', 'High', 'Critical'],
            'Status': ['Investigating', 'Resolved', 'Mitigated', 'Resolved', 'Blocked']
        })

        # Add color coding based on severity
        def get_severity_color(severity):
            colors = {'Critical': '#dc3545', 'High': '#fd7e14', 'Medium': '#ffc107', 'Low': '#28a745'}
            return colors.get(severity, '#6c757d')

        for idx, row in alerts_data.iterrows():
            st.markdown(f"""
            <div style="border-left: 4px solid {get_severity_color(row['Severity'])}; 
                        padding: 0.5rem; margin: 0.5rem 0; 
                        background-color: var(--background-color);
                        color: var(--text-color);">
                <strong>{row['Type']}</strong> - {row['Severity']}<br>
                <small>Source: {row['Source IP']} | {row['Timestamp'].strftime('%H:%M:%S')} | Status: {row['Status']}</small>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("System Information")

        st.markdown("""
        **Model Version:** v2.1.3  
        **Last Updated:** 2 hours ago  
        **Training Data:** 15M samples  
        **Features:** 42 network attributes  

        **Performance Metrics:**
        - Precision: 98.2%
        - Recall: 97.9%
        - F1-Score: 98.0%

        **System Health:**
        - CPU Usage: 45%
        - Memory: 2.1GB / 8GB
        - Disk: 120GB / 500GB
        """)

        if st.button("🔄 Refresh Dashboard", type="primary"):
            st.rerun()

    # Footer with last update time
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    show()

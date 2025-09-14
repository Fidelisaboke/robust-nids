"""
Main Streamlit Application - NIDS Overview Dashboard
"""
import streamlit as st

# Main app settings
st.set_page_config(
    page_title="NIDS Security Dashboard",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pages
pages = {
    "Dashboard": [
        st.Page("pages/overview.py", title="Overview", icon=":material/dashboard:"),
        st.Page("pages/live_monitor.py", title="Live Monitor", icon=":material/network_node:"),
    ],
    "Security Operations": [
        st.Page("pages/alerts.py", title="Security Alerts", icon=":material/warning:"),
        st.Page("pages/analytics.py", title="Threat Analytics", icon=":material/analytics:"),
    ],
    "Data & Models": [
        st.Page("pages/data_explorer.py", title="Data Explorer", icon=":material/dataset:"),
        st.Page("pages/model_management.py", title="Model Management", icon=":material/model_training:"),
    ],
    "Administration": [
        st.Page("pages/settings.py", title="Settings", icon=":material/settings:"),
    ]
}

# Navigation with top-level menu
navigation = st.navigation(
    pages,
    position="sidebar",
    expanded=True
)

# Common sidebar elements
with st.sidebar:
    st.header("NIDS Dashboard")
    st.markdown("---")
    # TODO: Add additional sidebar content that's common across pages

navigation.run()

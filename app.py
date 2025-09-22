"""
Main Streamlit Application - NIDS Overview Dashboard
"""

import streamlit as st
import time

from utils.auth import SessionManager, login_form

# Main app settings
st.set_page_config(
    page_title="NIDS Security Dashboard",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

session_manager = SessionManager()

# If not authenticated, show login form
if not session_manager.is_authenticated:
    # Hide sidebar completely when not authenticated
    st.markdown(
        """
        <style>
        .css-1d391kg {display: none}
        [data-testid="stSidebar"] {display: none}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Please log in to access the NIDS Security Dashboard")
    login_form(session_manager)
    st.stop()
else:
    # Only define pages and navigation when authenticated
    pages = {
        "Dashboard": [
            st.Page("views/overview.py", title="Overview", icon=":material/dashboard:"),
            st.Page(
                "views/live_monitor.py",
                title="Live Monitor",
                icon=":material/network_node:",
            ),
        ],
        "Security Operations": [
            st.Page("views/alerts.py", title="Security Alerts", icon=":material/warning:"),
            st.Page(
                "views/analytics.py",
                title="Threat Analytics",
                icon=":material/analytics:",
            ),
        ],
        "Data & Models": [
            st.Page(
                "views/data_explorer.py",
                title="Data Explorer",
                icon=":material/dataset:",
            ),
            st.Page(
                "views/model_management.py",
                title="Model Management",
                icon=":material/model_training:",
            ),
        ],
        "Administration": [
            st.Page("views/settings.py", title="Settings", icon=":material/settings:"),
        ],
    }

    # Refresh session
    session_manager.refresh_session()

    # Navigation with top-level menu
    navigation = st.navigation(pages, position="sidebar", expanded=True)

    with st.sidebar:
        st.header("NIDS Dashboard")

        # Current user information
        user = st.session_state["user"]
        roles = ", ".join(user["roles"])
        st.caption(f"Logged in as **{user.get('email')}** ({roles})")

        # Grace period popup
        if session_manager.needs_grace_prompt():
            st.warning("⚠️ Your session will expire soon!")
            if st.button("Extend Session", type="primary"):
                if session_manager.extend_session():
                    st.success("✅ Session extended")
                    st.rerun()

            # Refresh periodically to ensure grace period popup appears
            time.sleep(10)
            st.rerun()

        # Logout button
        if st.button("Log out"):
            session_manager.logout_user()

    navigation.run()

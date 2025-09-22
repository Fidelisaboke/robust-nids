"""
Main Streamlit Application - NIDS Overview Dashboard
"""

import streamlit as st
import time

from core.session import SessionManager
from core.mfa import MFAManager
from ui.components.login import show_login_page
from ui.components.mfa import show_mfa_page

# Main app settings
st.set_page_config(
    page_title="NIDS Security Dashboard",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session and MFA managers
session_manager = SessionManager()
mfa_manager = MFAManager(session_manager.config)

# Hide sidebar CSS for unauthenticated states
HIDE_SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] {display: none}
.stDeployButton {display: none}
#MainMenu {visibility: hidden}
footer {visibility: hidden}
</style>
"""


# Authentication flow
if not session_manager.is_session_valid:
    st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)

    if session_manager.is_awaiting_mfa():
        st.title("Two-Factor Authentication Required")
        show_mfa_page(session_manager, mfa_manager)
    else:
        st.title("Please log in to access the NIDS Security Dashboard")
        show_login_page(session_manager, mfa_manager)

    st.stop()


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
    user = session_manager.get_user_info()
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

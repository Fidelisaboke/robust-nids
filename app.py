"""
Main Streamlit Application - NIDS Overview Dashboard
"""

import time

import streamlit as st

from core.app_state import AppState
from core.mfa_manager import MFAManager
from core.session_manager import SessionManager
from ui.components.login_page import show_login_page, show_backup_code_warning
from ui.components.mfa_page import show_mfa_page

# Initialise Streamlit app state
app_state = AppState()
app_state.initialize()

# Main app settings
st.set_page_config(
    page_title="NIDS Security Dashboard",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialise session, and MFA managers
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

    # Check for pending MFA verification
    if session_manager.is_awaiting_mfa():
        st.title("Two-Factor Authentication Required")
        show_mfa_page(session_manager, mfa_manager)
    else:
        st.title("Please log in to access the NIDS Security Dashboard")
        show_login_page(session_manager, mfa_manager)

    st.stop()

# Show backup code warning (if used backup code for MFA)
if app_state.show_backup_code_warning:
    show_backup_code_warning(session_manager)
    st.stop()

# Enhanced pages configuration with proper user profile integration
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
        st.Page("views/settings.py", title="System Settings", icon=":material/settings:"),
        st.Page("views/user_profile.py", title="My Profile", icon=":material/person:"),
    ],
}

# Refresh session activity
session_manager.refresh_session()

# Navigation with top-level menu
navigation = st.navigation(pages, position="sidebar", expanded=True)

with st.sidebar:
    st.header("NIDS Dashboard")

    # Enhanced current user information
    user = session_manager.get_user_info()

    # Display username if available, fallback to email
    user_display_name = user.get("email")
    if user.get("first_name") and user.get("last_name"):
        user_display_name = f"{user['first_name']} {user['last_name']}"

    roles = ", ".join(user["roles"]) if user.get("roles") else "No roles"

    # User info with MFA status
    st.caption(f"👤 **{user_display_name}**")
    st.caption(f"🎯 {roles}")

    # Show MFA status badge
    if user.get("mfa_enabled"):
        st.success("🔒 MFA Enabled", icon="✅")
    else:
        st.warning("⚠️ MFA Not Enabled", icon="📱")

    # Session info
    time_remaining = session_manager.time_remaining()
    minutes, seconds = divmod(time_remaining, 60)
    st.caption(f"⏰ Session: {minutes:02d}:{seconds:02d} remaining")

    # Grace period popup - enhanced with better UX
    if session_manager.needs_grace_prompt():
        with st.container():
            st.error("⚠️ Session Expiring Soon!")

            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"Your session will expire in {time_remaining} seconds")
            with col2:
                if st.button("Extend Session", type="primary", use_container_width=True):
                    if session_manager.extend_session():
                        st.rerun()

            # Auto-refresh for countdown
            time.sleep(5)
            st.rerun()

    st.markdown("---")

    # Enhanced logout button
    if st.button("🚪 Log Out", use_container_width=True):
        session_manager.logout_user()

# Run the navigation
navigation.run()

# Auto-refresh session activity every 30 seconds for long-running pages
if time.time() - app_state.user["last_activity"] > 30:
    session_manager.refresh_session()
    user = session_manager.get_user_info()
    user["last_activity"] = time.time()
    session_manager.app_state.user = user

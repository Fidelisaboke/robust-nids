"""
Main Streamlit Application - NIDS Overview Dashboard
"""
import streamlit as st

from utils.auth import init_auth, login_form

# Main app settings
st.set_page_config(
    page_title="NIDS Security Dashboard",
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialise authentication state
init_auth()

# If not authenticated, show login form
if not st.session_state["authenticated"]:
    # Hide sidebar completely when not authenticated
    st.markdown("""
        <style>
        .css-1d391kg {display: none}
        [data-testid="stSidebar"] {display: none}
        </style>
        """, unsafe_allow_html=True)
    st.title("Please log in to access the NIDS Security Dashboard")
    login_form()
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
                "views/analytics.py", title="Threat Analytics", icon=":material/analytics:"
            ),
        ],
        "Data & Models": [
            st.Page(
                "views/data_explorer.py", title="Data Explorer", icon=":material/dataset:"
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

    # Navigation with top-level menu
    navigation = st.navigation(pages, position="sidebar", expanded=True)

    with st.sidebar:
        st.header("NIDS Dashboard")

        # Current user information
        user_info = st.session_state["user_info"]
        roles = ", ".join(user_info["roles"])
        st.caption(f"Logged in as **{user_info.get('email')}** ({roles})")

        # Logout button
        if st.button("Log out"):
            st.session_state["authenticated"] = False
            st.session_state["user_info"] = {}
            st.markdown('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)
            st.rerun()

    navigation.run()

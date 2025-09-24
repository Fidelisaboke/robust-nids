"""
User Profile Page - Personal settings and preferences
"""

import streamlit as st

from core.session_manager import SessionManager
from ui.components.user_profile import show_mfa_settings

session_manager = SessionManager()
auth_service = session_manager.auth_service


def show():
    """Render the user profile page"""

    # Check authentication
    user = session_manager.get_user_info()
    if not user:
        st.error("Please log in to access profile settings")
        return

    st.title("👤 User Profile Settings")

    # Profile tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Personal Information", "Security & MFA", "Preferences", "Session Management"])

    with tab1:
        show_personal_info(user)

    with tab2:
        show_security_settings(user)

    with tab3:
        show_user_preferences(user)

    with tab4:
        show_session_management(user)


def show_personal_info(user):
    """Display and edit personal information"""
    st.subheader("Personal Information")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            # First Name
            first_name = st.text_input("First Name", value=user.get("first_name", ""), help="Your legal first name")

            # Email (Disabled; read-only)
            st.text_input("Email Address", value=user.get("email", ""), type="default", disabled=True)

            # Department
            department = st.text_input(
                "Department", value=user.get("department", ""), help="Your organizational department"
            )

        with col2:

            # Last Name
            last_name = st.text_input("Last Name", value=user.get("last_name", ""), help="Your legal last name")

            # Job Title
            job_title = st.text_input("Job Title", value=user.get("job_title", ""), help="Your professional title")

        # Contact information
        st.markdown("#### Contact Information")
        phone = st.text_input("Phone Number", value=user.get("phone", ""))
        timezone = st.selectbox("Timezone", list_timezones(), index=get_timezone_index(user.get("timezone")))

        if st.form_submit_button("💾 Update Profile"):
            update_data = {
                "first_name": first_name,
                "last_name": last_name,
                "department": department,
                "job_title": job_title,
                "phone": phone,
                "timezone": timezone,
            }
            if update_user_profile(user["id"], update_data):
                st.success("Profile updated successfully!")
            else:
                st.error("Failed to update profile")


def show_security_settings(user):
    """Display security-related settings"""
    st.subheader("Security Settings")

    # Password management
    st.markdown("#### Password Management")
    if st.button("Change Password"):
        st.session_state.show_password_change = True

    if st.session_state.get("show_password_change", False):
        change_password_form()

    st.markdown("---")

    # MFA settings
    show_mfa_settings()

    st.markdown("---")

    # Session security
    st.markdown("#### Session Security")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Active Sessions", get_active_session_count(user["id"]))
        if st.button("View Active Sessions"):
            st.session_state.show_sessions = True

    with col2:
        st.metric("Last Login", format_last_login(user.get("last_login")))
        if st.button("Log Out Other Devices"):
            logout_other_sessions(user["id"])
            st.success("Other sessions logged out!")


def show_user_preferences(user):
    """Display user preference settings"""
    st.subheader(f"Application Preferences for {user['email']}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Dashboard Preferences**")
        default_view = st.selectbox(
            "Default Dashboard View", ["Overview", "Live Monitor", "Security Alerts", "Threat Analytics"], index=0
        )

        refresh_interval = st.selectbox(
            "Auto-refresh Interval", ["Off", "30 seconds", "1 minute", "5 minutes", "15 minutes"], index=2
        )

        theme_preference = st.radio("Theme Preference", ["System Default", "Light", "Dark"], index=0)

    with col2:
        st.markdown("**Notification Preferences**")
        email_notifications = st.checkbox("Email Notifications", value=True)
        browser_notifications = st.checkbox("Browser Notifications", value=True)

        st.markdown("**Alert Preferences**")
        critical_alerts = st.checkbox("Critical Alerts", value=True)
        high_priority = st.checkbox("High Priority Alerts", value=True)
        medium_priority = st.checkbox("Medium Priority Alerts", value=False)

    if st.button("Save Preferences"):
        # TODO: Implement actual saving of preferences
        preferences = {
            "dashboard": {
                "default_view": default_view,
                "refresh_interval": refresh_interval,
                "theme": theme_preference,
            },
            "notifications": {
                "email": email_notifications,
                "browser": browser_notifications,
                "critical_alerts": critical_alerts,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
            },
            "privacy": {"show_online_status": True, "share_analytics": False},
        }
        st.json(preferences)
        st.success("Preferences saved successfully!")


def show_session_management(user):
    """Display session management options"""
    st.subheader("Session Management")

    # Current session info
    st.markdown("**Current Session**")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Started:** {st.session_state.get('session_start', 'N/A')}")
    with col2:
        st.info(f"**Duration:** {get_session_duration()}")
    with col3:
        if st.button("🔄 Refresh Session"):
            st.rerun()

    # Active sessions table
    st.markdown("**Active Sessions**")
    sessions = get_user_sessions(user["id"])

    for session in sessions:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                current_indicator = "🟢 Current" if session["is_current"] else "⚪"
                st.write(f"{current_indicator} {session['device_info']}")
                st.caption(f"IP: {session['ip_address']} • Started: {session['start_time']}")
            with col2:
                st.write(f"Last active: {session['last_activity']}")
            with col3:
                if not session["is_current"] and st.button("Log Out", key=f"logout_{session['id']}"):
                    terminate_session(session["id"])
                    st.success("Session terminated!")
            with col4:
                if session["is_current"]:
                    st.button("Renew", key=f"renew_{session['id']}", disabled=True)

    st.markdown("---")
    if st.button("🚪 Log Out of All Devices", type="secondary"):
        logout_all_sessions(user["id"])
        st.success("Logged out of all devices!")
        # Redirect to login page
        st.session_state.authenticated = False
        st.rerun()


def get_session_duration():
    pass


def list_timezones():
    """Return list of common timezones"""
    return [
        "UTC",
        "US/Eastern",
        "US/Central",
        "US/Mountain",
        "US/Pacific",
        "Europe/London",
        "Europe/Paris",
        "Asia/Tokyo",
        "Asia/Shanghai",
    ]


def get_timezone_index(current_tz):
    """Get index for timezone selectbox"""
    timezones = list_timezones()
    return timezones.index(current_tz) if current_tz in timezones else 0


def update_user_profile(user_id: int, update_data: dict) -> bool:
    """Update user profile in database"""
    try:
        from services.auth import AuthService

        return AuthService.update_user_profile(user_id, update_data)
    except Exception as e:
        st.error(f"Error updating profile: {str(e)}")
        return False


# Placeholder functions for session management (to be implemented later)
def get_active_session_count(user_id: int) -> int:
    return 1  # TODO: Implement actual session counting


def format_last_login(last_login):
    return last_login.strftime("%Y-%m-%d %H:%M") if last_login else "Never"


def change_password_form():
    """Password change form"""
    with st.form("change_password"):
        st.subheader("Change Password")
        st.text_input("Current Password", type="password")  # TODO: Get value as 'current_pwd'
        new_pwd = st.text_input("New Password", type="password")
        confirm_pwd = st.text_input("Confirm New Password", type="password")

        if st.form_submit_button("Update Password"):
            if new_pwd != confirm_pwd:
                st.error("New passwords don't match")
            elif len(new_pwd) < 8:
                st.error("Password must be at least 8 characters")
            else:
                # TODO: Implement actual password change
                st.success("Password updated successfully!")
                st.session_state.show_password_change = False


def get_user_sessions(user_id: int):
    """Get user sessions - placeholder"""
    user_sessions = auth_service.get_user_sessions(user_id)
    return user_sessions  # TODO: Implement actual session retrieval


def terminate_session(session_id: str):
    """Terminate session - placeholder"""
    # TODO: Implement actual session termination
    st.success(f"Session terminated. ID: {session_id}")


def logout_other_sessions(user_id: int):
    """Logout other sessions - placeholder"""
    # TODO: Implement actual session logout
    user_sessions = auth_service.get_user_sessions(user_id)
    st.success(f"Logged out of {user_sessions}.")


def logout_all_sessions(user_id: int):
    """Logout all sessions - placeholder"""
    # TODO: Implement actual session logout
    user_sessions = auth_service.get_user_sessions(user_id)
    st.success(f"Logged out of {user_sessions}.")


if __name__ == "__main__":
    show()

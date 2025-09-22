import streamlit as st

from core.mfa import MFAManager
from core.session import SessionManager


def show_login_page(session_manager: SessionManager, mfa_manager: MFAManager):
    """Display the complete login page with security notices and form."""
    # Security header
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1f4e79 0%, #2d5aa0 100%);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #ff6b35;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="color: white; margin: 0 0 10px 0; display: flex; align-items: center;">
                🔒 AUTHORIZED ACCESS ONLY
            </h3>
            <p style="color: #e0e6ed; margin: 0; font-size: 14px; line-height: 1.4;">
                You are accessing a secure Network Intrusion Detection System (NIDS).
                This system is restricted to authorized personnel only.
                All activities are monitored and logged.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Login form
    st.markdown("### 🔐 System Login")

    with st.form("login"):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="Use your authorized system email address.",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Enter your secure system password.",
        )

        # Some spacing
        st.write("")

        # Login button
        if st.form_submit_button("🔓 Access System", use_container_width=True, type="primary"):
            _handle_login_attempt(session_manager, mfa_manager, email, password)

    # Security footer
    st.markdown(
        """
        <div style="
            margin-top: 30px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 3px solid #6c757d;
        ">
            <small style="color: #6c757d;">
                <strong>Security Reminders:</strong><br>
                • Do not share your login credentials<br>
                • Log out when finished<br>
                • Report suspicious activity immediately<br>
                • This session will timeout after inactivity
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _handle_login_attempt(session_manager: SessionManager, mfa_manager: MFAManager, email: str, password: str):
    """Process login attempt and handle authentication flow."""
    # Basic validation
    if not email or not password:
        st.error("⚠️ Both email and password are required")
        return

    try:
        # Authentication attempt
        auth_service = session_manager.auth_service
        user_data, error = auth_service.authenticate(email, password)

        if error:
            st.error(f"🚫 {error}")
            return

        # Get the user object
        user = auth_service.get_user_by_id(user_data["id"])

        # Handle MFA or direct login
        if mfa_manager.should_prompt_mfa(user):
            mfa_manager.store_pending_auth(user)
        else:
            session_manager.login_user(user)
            st.success("✅ Login successful")

        st.rerun()

    except Exception as e:
        st.error(f"🚫 Authentication error: {str(e)}")

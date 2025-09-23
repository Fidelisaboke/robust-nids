import streamlit as st

from core.mfa import MFAManager
from core.session import SessionManager

# HTML template for MFA header
MFA_HEADER_HTML = """
<div style="
    background: linear-gradient(135deg, #2d5aa0 0%, #1f4e79 100%);
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #ff6b35;
    margin-bottom: 20px;
">
    <h4 style="color: white; margin: 0; display: flex; align-items: center;">
        🔒 Additional Verification Required
    </h4>
</div>
"""


def show_mfa_page(session_manager: SessionManager, mfa_manager: MFAManager):
    """Display the MFA verification page."""
    # MFA header
    st.markdown(MFA_HEADER_HTML, unsafe_allow_html=True)

    st.title("Two-Factor Authentication")
    st.info("Check your authenticator app for the 6-digit code")

    # Handle max attempts
    if mfa_manager.is_max_attempts_reached():
        st.error("🚫 Too many failed attempts. Please try logging in again.")
        if st.button("Return to Login"):
            session_manager.clear_pending_auth()
            st.rerun()
        return

    # MFA code input
    with st.form("mfa_verification"):
        code = st.text_input(
            "Enter 6-digit code",
            type="password",
            max_chars=6,
            placeholder="000000",
            help="Enter the code from your authenticator app",
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            verify_clicked = st.form_submit_button("Verify Code", type="primary")

        with col2:
            cancel_clicked = st.form_submit_button("Cancel Login")

    # Handle form submissions
    if verify_clicked and code:
        _verify_mfa_code(session_manager, mfa_manager, code)
    elif cancel_clicked:
        session_manager.clear_pending_auth()
        st.rerun()

    # Back to log in option
    if st.button("← Back to Login", type="secondary"):
        session_manager.clear_pending_auth()
        st.rerun()


def _verify_mfa_code(session_manager: SessionManager, mfa_manager: MFAManager, code: str):
    """Verify the MFA code and handle the result."""
    user_data = session_manager.get_pending_user()
    if not user_data:
        st.error("Session expired. Please login again.")
        return

    try:
        if session_manager.verify_mfa(code):
            session_manager.login_user(user_data)
            session_manager.clear_pending_auth()
            st.success("✅ Authentication successful")
            st.rerun()
        else:
            mfa_manager.increment_attempts()
            remaining = mfa_manager.get_remaining_attempts()
            st.error(f"❌ Invalid code. {remaining} attempts remaining.")

    except Exception as e:
        st.error(f"🚫 Verification error: {str(e)}")

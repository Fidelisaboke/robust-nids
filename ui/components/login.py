import streamlit as st

from core.mfa import MFAManager
from core.session import SessionManager
from services.auth import AuthService


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

    st.markdown("---")
    with st.expander("🔑 Lost Access to Your Authenticator?"):
        st.write("If you don't have access to your authenticator app, you can use a backup code.")
        if st.button("Use Backup Code Instead", key="use_backup_code"):
            st.session_state.show_backup_code_login = True
            st.rerun()

    # Show backup code login if requested
    if st.session_state.get("show_backup_code_login"):
        show_backup_code_login(session_manager)
        return

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

        # Handle MFA verification
        user = auth_service.get_user_by_id(user_data["id"])
        if mfa_manager.should_prompt_mfa(user):
            mfa_manager.store_pending_auth(user_data)
        else:
            session_manager.login_user(user_data)
            st.success("✅ Login successful")

        st.rerun()

    except Exception as e:
        st.error(f"🚫 Authentication error: {str(e)}")


def show_backup_code_login(session_manager: SessionManager):
    """Backup code login flow"""
    st.subheader("🔑 Login with Backup Code")

    with st.form("backup_code_login"):
        email = st.text_input("Email Address", placeholder="your@email.com")
        backup_code = st.text_input(
            "Backup Code", placeholder="8-character backup code", help="Enter one of your backup codes (case-sensitive)"
        )

        if st.form_submit_button("Login with Backup Code", type="primary"):
            if authenticate_with_backup_code(email, backup_code, session_manager):
                st.success("Login successful!")
                st.rerun()

    if st.button("← Back to Regular Login"):
        st.session_state.show_backup_code_login = False
        st.rerun()


def authenticate_with_backup_code(email: str, backup_code: str, session_manager: SessionManager) -> bool:
    """Handle backup code authentication"""
    if not email or not backup_code:
        st.error("Please enter both email and backup code")
        return False

    try:
        user_data, error = AuthService.authenticate_with_backup_code(email, backup_code)

        if error:
            st.error(f"🚫 {error}")
            return False

        # Login user
        session_manager.login_user(user_data)

        # Show important warning if backup code was used
        if user_data.get("used_backup_code"):
            st.session_state.show_backup_code_warning = True

        return True

    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False


def show_backup_code_warning(session_manager: SessionManager):
    """Warning shown after logging in with backup code"""
    st.warning("🚨 IMPORTANT SECURITY NOTICE")
    st.title("Backup Code Used")

    st.write(
        """
    ### You have logged in using a backup code.

    **This indicates you may have lost access to your authenticator device.**

    ### Required Actions:
    1. **Generate new backup codes** (old ones are now invalid)
    2. **Reconfigure MFA** with your new authenticator device
    3. **Securely store** your new backup codes
    """
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Generate New Backup Codes", type="primary", use_container_width=True):
            result = AuthService.generate_new_backup_codes(session_manager.get_user_id())
            if result["success"]:
                st.session_state.backup_codes = result["backup_codes"]
                st.session_state.show_new_backup_codes = True
                st.rerun()

    with col2:
        if st.button("Configure New MFA Device", use_container_width=True):
            st.session_state.show_mfa_setup = True
            st.session_state.mfa_setup_complete = False
            st.rerun()

    # Show new backup codes if generated
    if st.session_state.get("show_new_backup_codes"):
        show_new_backup_codes()

    st.markdown("---")
    if st.button("⚠️ Acknowledge and Continue", type="secondary"):
        del st.session_state.show_backup_code_warning
        st.rerun()


def show_new_backup_codes():
    """Display new backup codes one-time with secure copy options"""
    backup_codes = st.session_state.get("backup_codes", [])

    with st.container(border=True):
        st.warning(
            """
        ⚠️ **CRITICAL: Save these new backup codes now!**

        These codes are displayed **ONCE** and cannot be recovered.
        Store them in a secure password manager or print them.
        """
        )

        # Display codes in a secure format
        st.subheader("Your New Backup Codes")

        col1, col2 = st.columns(2)

        with col1:
            # Copy to clipboard (with security warning)
            codes_text = "\n".join([f"{i + 1:02d}. {code}" for i, code in enumerate(backup_codes)])
            st.download_button(
                label="📥 Download as Text File",
                data=codes_text,
                file_name="nids_backup_codes.txt",
                mime="text/plain",
                help="Download encrypted backup codes for secure storage",
            )

        with col2:
            # One-time view confirmation
            if st.button("✅ I Have Saved My Codes", type="primary", use_container_width=True):
                # Clear backup codes from session
                del st.session_state["backup_codes"]
                del st.session_state["show_new_backup_codes"]
                del st.session_state["show_backup_code_warning"]
                st.rerun()

        # Security reminders
        st.info(
            """
        **Security Best Practices:**
        - Store backup codes in a password manager
        - Do not save in plain text files on your computer
        - Consider printing and storing in a secure physical location
        - Never share these codes with anyone
        """
        )

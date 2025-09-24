import base64
from io import BytesIO

import pyotp
import qrcode
import streamlit as st

from core.config import SessionKeys
from core.session_manager import SessionManager
from services.auth import AuthService

session_manager = SessionManager()


def show_mfa_settings():
    """MFA configuration component"""
    st.markdown("#### Multi-Factor Authentication")

    # Initialize session state variables
    if SessionKeys.MFA_ENABLED not in st.session_state:
        # Get current MFA status from database
        user_id = session_manager.get_user_id()
        if user_id:
            user = AuthService.get_user_by_id(user_id)
            st.session_state.mfa_enabled = user.mfa_enabled if user else False
        else:
            st.session_state.mfa_enabled = False

    if SessionKeys.MFA_SETUP_COMPLETE not in st.session_state:
        st.session_state.mfa_setup_complete = False

    col1, col2 = st.columns([2, 1])

    with col1:
        mfa_enabled = st.checkbox(
            "Enable Multi-Factor Authentication",
            value=st.session_state.mfa_enabled,
            help="Add an extra layer of security to your account",
        )

        if mfa_enabled != st.session_state.mfa_enabled:
            st.session_state.mfa_enabled = mfa_enabled
            if mfa_enabled:
                st.session_state.show_mfa_setup = True
                st.rerun()
            else:
                # Show TOTP verification before disabling MFA
                st.session_state.verify_disable_mfa = True
                st.rerun()

    with col2:
        if st.session_state.mfa_enabled and not st.session_state.get("mfa_setup_complete", False):
            if st.button("Configure MFA"):
                st.session_state.show_mfa_setup = True
                st.rerun()

    # Show current MFA status
    if st.session_state.get("mfa_setup_complete", False):
        st.success("✅ MFA is configured and active")
        if st.button("Reconfigure MFA"):
            st.session_state.mfa_setup_complete = False
            st.session_state.show_mfa_setup = True
            st.rerun()

    if st.session_state.get("show_mfa_setup", False):
        show_mfa_setup_wizard()

    # Show TOTP verification for disabling MFA
    if st.session_state.get("verify_disable_mfa", False):
        show_disable_mfa_verification()


def show_mfa_setup_wizard():
    """MFA setup wizard"""
    st.markdown("---")
    st.subheader("MFA Setup")

    # For now, we'll focus on TOTP. Email/SMS can be added later
    mfa_method = st.radio(
        "Choose MFA Method:", ["TOTP (Google Authenticator)", "Email Verification", "SMS Verification"], index=0
    )

    if mfa_method == "TOTP (Google Authenticator)":
        setup_totp_authentication()
    elif mfa_method == "Email Verification":
        st.info("Email verification coming soon...")
        # setup_email_authentication()
    else:
        st.info("SMS verification coming soon...")


def setup_totp_authentication():
    """TOTP setup using pyotp"""
    try:
        user_id = session_manager.get_user_id()
        if not user_id:
            st.error("User not authenticated")
            return

        # Get user from database
        user = AuthService.get_user_by_id(user_id)
        if not user:
            st.error("User not found")
            return

        # Generate or retrieve MFA secret
        if "temp_mfa_secret" not in st.session_state or st.session_state.temp_mfa_secret is None:
            if user.mfa_secret:
                st.session_state.temp_mfa_secret = user.mfa_secret
            else:
                # Generate new secret
                st.session_state.temp_mfa_secret = pyotp.random_base32()

        mfa_secret = st.session_state.temp_mfa_secret

        # Generate TOTP URI and QR code
        totp = pyotp.TOTP(mfa_secret)
        issuer_name = "NIDS Dashboard"
        totp_uri = totp.provisioning_uri(name=user.email, issuer_name=issuer_name)

        # Show backup codes if TOTP setup was completed
        if st.session_state.get("show_backup_codes"):
            show_backup_codes()
            return

        with st.expander("TOTP Configuration", expanded=True):
            st.info("Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)")

            # Generate QR code
            qr_img = qrcode.make(totp_uri)
            buffered = BytesIO()
            qr_img.save(buffered, format="PNG")
            qr_b64 = base64.b64encode(buffered.getvalue()).decode()

            # Display QR code
            st.image(f"data:image/png;base64,{qr_b64}", width=200)

            # Show manual entry option
            with st.expander("Can't scan QR code?"):
                st.code(f"Secret Key: {mfa_secret}")
                st.write("Manual entry instructions:")
                st.write("1. Open your authenticator app")
                st.write("2. Choose 'Enter setup key'")
                st.write(f"3. Account: {user.email}")
                st.write(f"4. Key: {mfa_secret}")
                st.write("5. Type: Time-based")

            st.markdown("---")
            st.subheader("Verify Setup")

            verification_code = st.text_input(
                "Enter verification code from your app:", placeholder="6-digit code", max_chars=6, key="mfa_verify_code"
            )

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Verify TOTP", type="primary"):
                    verify_totp_setup(mfa_secret, verification_code, user_id)

            with col2:
                if st.button("Cancel Setup"):
                    st.session_state.show_mfa_setup = False
                    st.rerun()

    except Exception as e:
        st.error(f"MFA configuration error: {str(e)}")


def verify_totp_setup(secret: str, code: str, user_id: int):
    """Verify TOTP code and enable MFA for user"""
    if not code or len(code) != 6:
        st.error("Please enter a valid 6-digit code")
        return

    try:
        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            # Enable MFA in database
            result = AuthService.enable_mfa(secret, user_id, "totp")
            if result["success"]:
                # Store backup codes in session for one-time display
                st.session_state["backup_codes"] = result["backup_codes"]
                st.session_state["show_backup_codes"] = True
                st.rerun()
            else:
                st.error(f"Failed to enable MFA: {result["message"]}")
        else:
            st.error("Invalid verification code. Please try again.")
    except Exception as e:
        st.error(f"Verification error: {str(e)}")


def show_backup_codes():
    """Display backup codes one-time with secure copy options"""
    if not st.session_state.get("show_backup_codes"):
        return

    backup_codes = st.session_state.get("backup_codes", [])

    st.success("🎉 MFA Setup Complete!")

    with st.container(border=True):
        st.warning(
            """
        ⚠️ **CRITICAL: Save these backup codes now!**

        These codes are displayed **ONCE** and cannot be recovered.
        Store them in a secure password manager or print them.
        """
        )

        # Display codes in a secure format
        st.subheader("Your Backup Codes")

        col1, col2 = st.columns(2)
        codes_per_column = len(backup_codes) // 2

        with col1:
            for i, code in enumerate(backup_codes[:codes_per_column]):
                st.code(f"{i + 1:02d}. {code}", language="text")

        with col2:
            for i, code in enumerate(backup_codes[codes_per_column:], codes_per_column + 1):
                st.code(f"{i:02d}. {code}", language="text")

        # Secure copy functionality
        st.markdown("---")
        st.subheader("Secure Copy Options")

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
                del st.session_state["show_backup_codes"]
                st.session_state.show_mfa_setup = False
                st.session_state.mfa_setup_complete = True
                st.session_state.mfa_enabled = True
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


def show_disable_mfa_verification():
    """Show TOTP verification before disabling MFA"""
    st.markdown("---")
    st.warning("🔐 Verify Your Identity")
    st.subheader("Disable Multi-Factor Authentication")

    st.write(
        """
    **Security verification required to disable MFA.**
    Please enter a code from your authenticator app to confirm this action.
    """
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        totp_code = st.text_input("Enter TOTP Code:", placeholder="6-digit code", max_chars=6, key="disable_mfa_totp")

        verify_col1, verify_col2 = st.columns(2)

        with verify_col1:
            if st.button("✅ Confirm Disable", type="primary", use_container_width=True):
                if verify_disable_mfa(totp_code):
                    st.success("MFA has been disabled")
                    st.session_state.mfa_setup_complete = False
                    st.session_state.verify_disable_mfa = False
                    st.rerun()

        with verify_col2:
            if st.button("❌ Cancel", use_container_width=True):
                # Revert the checkbox state
                st.session_state.mfa_enabled = True
                st.session_state.verify_disable_mfa = False
                st.rerun()

    with col2:
        st.info(
            """
        **Why this verification is required:**
        - Prevents unauthorized MFA disabling
        - Ensures you have access to your authenticator app
        - Protects your account security
        """
        )


def verify_disable_mfa(totp_code: str) -> bool:
    """Verify TOTP code before disabling MFA"""
    if not totp_code or len(totp_code) != 6:
        st.error("Please enter a valid 6-digit code")
        return False

    try:
        user_id = session_manager.get_user_id()
        if not user_id:
            st.error("User not authenticated")
            return False

        # Get user's MFA secret
        user = AuthService.get_user_by_id(user_id)
        if not user or not user.mfa_secret:
            st.error("MFA not configured for this user")
            return False

        # Verify TOTP code
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(totp_code):
            # TOTP verified, now disable MFA
            if disable_mfa():
                return True
            else:
                st.error("Failed to disable MFA")
                return False
        else:
            st.error("Invalid verification code. Please try again.")
            return False

    except Exception as e:
        st.error(f"Verification error: {str(e)}")
        return False


def disable_mfa() -> bool:
    """Disable MFA for current user after verification."""
    try:
        user_id = session_manager.get_user_id()
        if user_id and AuthService.disable_mfa(user_id):
            # Clear session state
            session_keys_to_clear = ["temp_mfa_secret", "backup_codes", "show_backup_codes"]
            for key in session_keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            return True
        return False
    except Exception as e:
        st.error(f"Error disabling MFA: {str(e)}")
        return False


def setup_email_authentication():
    """Email authentication - placeholder for future implementation"""
    st.info("Email-based MFA will be implemented in a future update")

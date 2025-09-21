"""
Login page and auth helpers for the Streamlit NIDS dashboard.
"""

from datetime import datetime

import streamlit as st

from services.auth import AuthService


class SessionManager:
    """Class for handling auth sessions in the Streamlit dashboard."""

    # Default non-authenticated user properties
    _default_user_dict = {
        "id": None,
        "email": None,
        "roles": [],
        "login_time": None,
    }

    def __init__(self):
        self.auth_service = AuthService()
        self._init_auth()

    @property
    def is_authenticated(self):
        user = st.session_state["user"]
        if not user["id"] or not user["login_time"]:
            return False

        return True

    def _init_auth(self):
        if "user" not in st.session_state:
            st.session_state.user = self._default_user_dict.copy()

    def login_user(self, email, password):
        user, error = self.auth_service.authenticate(email, password)
        if user:
            now_ts = datetime.now().timestamp()
            st.session_state["user"] = {
                "id": user["id"],
                "email": user["email"],
                "roles": user["roles"],
                "login_time": now_ts,
            }
            return {"success": True, "message": "Authentication successful. Redirecting..."}
        else:
            return {"success": False, "message": f"Authentication failed: {error}"}

    def logout_user(self, reason="Logged out"):
        st.session_state["user"] = self._default_user_dict.copy()
        st.warning(reason)
        st.markdown('<meta http-equiv="refresh" content="0;url=/">', unsafe_allow_html=True)
        st.rerun()


def login_form(session_manger: SessionManager):
    # Security notice styling
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

        # Full-width login button
        submitted = st.form_submit_button("🔓 Access System", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("⚠️ Both email and password are required")
            else:
                result = session_manger.login_user(email, password)
                if result["success"]:
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                else:
                    st.error(f"🚫 {result['message']}")

    # Footer with security reminders
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

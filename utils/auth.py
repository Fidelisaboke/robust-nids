"""
Login page and auth helpers for the Streamlit NIDS dashboard.
"""

import streamlit as st

from services.auth import AuthService


def init_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}


def login_form():
    auth_service = AuthService()

    # Security notice styling
    st.markdown("""
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
                This system is restricted to authorized personnel only. All activities are monitored and logged.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔐 System Login")

    with st.form("login"):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="Use your authorized system email address."
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Enter your secure system password."
        )

        # Some spacing
        st.write("")

        # Full-width login button
        submitted = st.form_submit_button(
            "🔓 Access System",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            if not email or not password:
                st.error("⚠️ Both email and password are required")
            else:
                user_info, error = auth_service.verify_login(email, password)
                if user_info:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = user_info
                    st.success("✅ Authentication successful. Redirecting...")
                    st.rerun()
                else:
                    st.error(f"🚫 {error}")

    # Footer with security reminders
    st.markdown("""
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
    """, unsafe_allow_html=True)

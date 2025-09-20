import streamlit as st

from services.auth import AuthService


def init_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user_info" not in st.session_state:
        st.session_state.user_info = {}


def login_form():
    auth_service = AuthService()

    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password")
        submitted = st.form_submit_button("Login")

        if submitted:
            user_info, error = auth_service.verify_login(email, password)
            if user_info:
                st.session_state["authenticated"] = True
                st.session_state["user_info"] = user_info
                st.rerun()
            else:
                st.error(error)

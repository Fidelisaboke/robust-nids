import streamlit as st


# --- TOTP Dialog Component ---
@st.dialog("TOTP Verification", dismissible=False)
def show_totp_dialog(
    prompt="Enter your 6-digit TOTP code",
    on_success=None,
    on_cancel=None,
    session_key="totp_dialog_result",
    verify_func=None,
    error_message="Invalid code. Please try again.",
    key_prefix="totp",
):
    st.markdown(f"#### {prompt}")
    input_key = f"{key_prefix}_code_input"
    verify_key = f"{key_prefix}_verify_btn"
    cancel_key = f"{key_prefix}_cancel_btn"
    code = st.text_input("TOTP Code", max_chars=6, type="password", key=input_key)
    submitted = st.button("Verify", key=verify_key, use_container_width=True)
    cancelled = st.button("Cancel", key=cancel_key, use_container_width=True, type="primary")
    error = st.session_state.get("totp_dialog_error", "")

    if error:
        st.error(error)
    if submitted:
        if verify_func and not verify_func(code):
            st.session_state["totp_dialog_error"] = error_message
        else:
            st.session_state[session_key] = code
            st.session_state["totp_dialog_error"] = ""
            if on_success:
                on_success(code)
            st.rerun()  # Only close dialog on success
    if cancelled:
        st.session_state["totp_dialog_error"] = ""
        if on_cancel:
            on_cancel()
        st.rerun()  # Only close dialog on cancel

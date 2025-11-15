import email
import re


def extract_html_body_from_mime(mime_message):
    """Extract HTML body from mime message

    Args:
        mime_message: The mime message from fastapi-mail outbox

    Returns:
        The HTML body content or None
    """
    msg = email.message_from_string(str(mime_message))
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                return payload.decode("utf-8")

    return None


def extract_token_from_email(email_content, token_type="verification"):
    """Extract token from email body for both verification and reset

    Args:
        email_content: Content of the email
        token_type (str, optional): Type of token to extract. Defaults to "verification".

    Returns:
        Extracted token or None
    """
    match = re.search(r"token=([\w\-\.]+)", email_content)
    return match.group(1) if match else None

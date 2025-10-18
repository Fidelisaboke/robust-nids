from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str


class EmailTemplateData(BaseModel):
    recipient_name: Optional[str] = None
    action_url: Optional[str] = None
    support_email: Optional[str] = None
    additional_data: Dict[str, Any] = {}

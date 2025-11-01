from typing import Annotated

from pydantic import BaseModel, EmailStr, constr


class MFASetupResponse(BaseModel):
    qr_code: str
    secret: str
    totp_uri: str


class MFAVerifyPayload(BaseModel):
    code: Annotated[str, constr(strip_whitespace=True, min_length=4, max_length=32)]


class MFAEnablePayload(BaseModel):
    verification_code: Annotated[str, constr(strip_whitespace=True, min_length=4, max_length=32)]
    temp_secret: Annotated[str, constr(strip_whitespace=True, min_length=16, max_length=64)]


class MFAEnableResponse(BaseModel):
    backup_codes: list[str]
    detail: str = "MFA has been enabled successfully."


class MFADisableResponse(BaseModel):
    detail: str = "MFA has been disabled successfully."


class MFARecoveryInitiateRequest(BaseModel):
    email: EmailStr


class MFARecoveryInitiateResponse(BaseModel):
    detail: str = "If the email is registered, a recovery link has been sent."


class MFARecoveryCompleteRequest(BaseModel):
    mfa_recovery_token: Annotated[str, constr(strip_whitespace=True, max_length=255)]


class MFARecoveryCompleteResponse(BaseModel):
    detail: str = "MFA recovery successful. Please log in and set up MFA again."

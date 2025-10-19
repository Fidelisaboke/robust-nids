from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class MFAChallengeResponse(BaseModel):
    mfa_required: bool = True
    mfa_challenge_token: str


class EmailVerificationRequiredResponse(BaseModel):
    email_verified: bool
    email: EmailStr
    detail: str = "Email verification is required before logging in."


LoginResponse = TokenResponse | MFAChallengeResponse | EmailVerificationRequiredResponse


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str
    mfa_code: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str

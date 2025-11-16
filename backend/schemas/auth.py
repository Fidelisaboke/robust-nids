from pydantic import BaseModel, EmailStr

from schemas.users import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut | None = None


class MFAChallengeResponse(BaseModel):
    mfa_required: bool = True
    mfa_challenge_token: str


class EmailVerificationRequiredResponse(BaseModel):
    email_verified: bool
    email: EmailStr
    detail: str = "Email verification is required before logging in."


LoginResponse = TokenResponse | MFAChallengeResponse | EmailVerificationRequiredResponse


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    phone: str | None = None
    department: str | None = None
    job_title: str | None = None


class UserRegistrationResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    detail: str


class RefreshRequest(BaseModel):
    refresh_token: str


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


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    mfa_code: str | None = None

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class MFARequiredResponse(BaseModel):
    mfa_required: bool = True
    user_id: int


class RefreshRequest(BaseModel):
    refresh_token: str

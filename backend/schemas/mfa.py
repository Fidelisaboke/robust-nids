from pydantic import BaseModel, EmailStr


class MFAVerifyPayload(BaseModel):
    code: str


class MFAEnablePayload(BaseModel):
    verification_code: str
    temp_secret: str


class MFARecoveryInitiateRequest(BaseModel):
    email: EmailStr


class MFARecoveryCompleteRequest(BaseModel):
    token: str

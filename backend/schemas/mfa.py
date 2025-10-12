from typing import Annotated

from pydantic import BaseModel, EmailStr, constr


class MFAVerifyPayload(BaseModel):
    code: Annotated[str, constr(strip_whitespace=True, min_length=4, max_length=32)]


class MFAEnablePayload(BaseModel):
    verification_code: Annotated[str, constr(strip_whitespace=True, min_length=4, max_length=32)]
    temp_secret: Annotated[str, constr(strip_whitespace=True, min_length=16, max_length=64)]


class MFARecoveryInitiateRequest(BaseModel):
    email: EmailStr


class MFARecoveryCompleteRequest(BaseModel):
    token: Annotated[str, constr(strip_whitespace=True, max_length=255)]

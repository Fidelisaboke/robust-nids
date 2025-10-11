from pydantic import BaseModel


class MFAVerifyPayload(BaseModel):
    code: str

class MFAEnablePayload(BaseModel):
    verification_code: str
    temp_secret: str

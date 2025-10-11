from pydantic import BaseModel


class MFAVerifyPayload(BaseModel):
    user_id: int
    code: str

class MFAEnablePayload(BaseModel):
    verification_code: str
    temp_secret: str

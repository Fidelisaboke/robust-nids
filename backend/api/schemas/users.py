from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from .roles import RoleOut


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = None
    preferences: dict
    profile_completed: bool
    last_profile_update: Optional[str] = None
    email_verified: bool
    phone_verified: bool
    role: Optional[List[RoleOut]] = None
    created_at: datetime
    last_login: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

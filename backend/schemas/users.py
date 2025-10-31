from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from schemas.roles import RoleOut


class UserOut(BaseModel):
    id: int
    email: EmailStr
    mfa_enabled: bool
    mfa_configured_at: Optional[datetime]
    mfa_method: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = None
    preferences: dict
    profile_completed: bool
    last_profile_update: Optional[datetime] = None
    email_verified: bool
    phone_verified: bool
    roles: Optional[List[RoleOut]] = None
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = None
    roles: Optional[List[int]] = None  # List of role IDs
    preferences: Optional[dict] = {}
    is_active: bool


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = None
    roles: Optional[List[int]] = None  # List of role IDs
    preferences: Optional[dict] = {}
    is_active: Optional[bool] = None

class UserRoleUpdateRequest(BaseModel):
    roles: list[int] | None = None


class UserRoleUpdateResponse(BaseModel):
    detail: str
    user: UserOut

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.users import UserOut
from utils.enums import AlertSeverity, AlertStatus, ReportStatus


class ReportCreate(BaseModel):
    """Schema for creating a new report request."""
    title: str
    start_date: datetime
    end_date: datetime
    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Weekly Security Report",
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": "2024-01-07T23:59:59Z",
                    "severity": "high",
                    "status": "active",
                }
            ]
        }
    )

    @field_validator("start_date", "end_date", mode="after")
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

class ReportOut(BaseModel):
    """Schema for returning a report object."""
    id: int
    title: str
    status: ReportStatus
    parameters: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    owner: UserOut
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from typing import Any

from pydantic import BaseModel


class EmailTemplateData(BaseModel):
    recipient_name: str | None = None
    action_url: str | None = None
    support_email: str | None = None
    additional_data: dict[str, Any] = {}

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import UTC, datetime


class LifeCycle(BaseModel):
    creator: str = Field(..., description="생성자 ID 또는 이름")
    updater: Optional[str] = Field(default=None, description="수정자 ID 또는 이름")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="생성 일시 (UTC, timezone-aware)",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="수정 일시 (UTC, timezone-aware)",
    )

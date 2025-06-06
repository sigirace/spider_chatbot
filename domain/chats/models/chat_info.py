from typing import Annotated

from pydantic import BaseModel, Field

from datetime import UTC, datetime
from domain.chats.models.identifiers import ChatId


class ChatInfo(BaseModel):
    class Config:
        populate_by_name = True

    id: Annotated[
        ChatId | None, Field(max_length=100, alias="_id", description="채팅의 식별자")
    ] = Field(
        default=None,  # 이 None 의 경우는 로컬에서만 다뤄져야 함.
    )
    owner_id: Annotated[str, Field(max_length=100)] = Field(
        description="채팅 소유자의 식별자"
    )
    title: Annotated[str | None, Field(max_length=100)] = Field(
        default=None, description="채팅의 타이틀"
    )
    created_at: Annotated[datetime, Field(description="채팅 생성시간")] = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    is_hidden: Annotated[bool, ...] = Field(
        default=False, description="유저에게 이 채팅이 감춰질 것인지의 여부"
    )

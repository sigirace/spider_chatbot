from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field

from domain.chats.models.identifiers import ChatId


class ChatInfoResponse(BaseModel):
    """
    ChatInfo 를 외부에 전달하기 위한 DTO
    """

    id: Annotated[ChatId, ...] = Field(description="채팅의 식별자")
    owner_id: Annotated[str, Field(max_length=100)] = Field(
        description="채팅 소유자의 식별자"
    )
    title: Annotated[str | None, Field(max_length=100)] = Field(
        description="채팅의 타이틀"
    )
    created_at: datetime


class ChatInfoListResponse(BaseModel):
    """
    전체 ChatInfo 리스트를 전달하기 위한 DTO
    """

    chat_info_list: list[ChatInfoResponse]


class SlicedChatInfoListResponse(BaseModel):
    """
    슬라이싱된 ChatInfo 리스트를 전달하기 위한 DTO
    """

    chat_info_list: list[ChatInfoResponse]
    next_start_offset: int | None

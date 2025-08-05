from typing import Annotated, Literal, Optional
from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from fastapi import Query


from domain.api.models import RerankOutput
from domain.messages.models.identifiers import MessageId
from domain.plans.plan import PlanInfo


class MessagesRequestBody(BaseModel):
    user_query: Annotated[str, Query(max_length=10240)]


class AudioRequestBody(BaseModel):
    user_query: Optional[str] = Field(default=None, description="사용자 질의")
    audio_path: Optional[str] = Field(default=None, description="오디오 경로")

    @model_validator(mode="after")
    def validate_either_field_present(cls, values):
        if not values.user_query and not values.audio_path:
            raise ValueError("user_query 또는 audio_path 중 하나는 반드시 필요합니다.")
        return values


class BaseMessageResponse(BaseModel):
    """
    Message 를 외부에 전달하기 위한 DTO의 베이스
    """

    id: Annotated[MessageId, ...] = Field(
        description="메시지의 식별자. id는 외부에 전달될 때 반드시 지정되어 있어야 한다"
    )
    role: Annotated[
        Literal["system", "user", "assistant"],
        Field(description="메시지의 발생 주체"),
    ]
    content: Annotated[str | None, ...] = Field(description="메시지의 내용")
    metadata: Annotated[dict[str, str], ...]
    created_at: datetime


class SystemMessageResponse(BaseMessageResponse):
    """
    SystemMessage 를 외부에 전달하기 위한 DTO
    """

    pass


class HumanMessageResponse(BaseMessageResponse):
    """
    HumanMessage 를 외부에 전달하기 위한 DTO
    """

    pass


class AIMessageResponse(BaseMessageResponse):
    """
    AIMessage 를 외부에 전달하기 위한 DTO
    """

    status: Annotated[
        str,
        Field(description="메시지의 처리 상태"),
    ]
    plan: Annotated[PlanInfo | None, ...] = Field(
        description="메시지의 처리 계획 및 도중의 결과"
    )
    primary_page_list: Annotated[list[RerankOutput] | None, ...] = Field(
        default=None, description="메시지의 주요 페이지"
    )


class MessageListResponse(BaseModel):
    """
    전체 메시지 리스트를 전달하기 위한 DTO
    """

    message_list: list[
        BaseMessageResponse
        | SystemMessageResponse
        | HumanMessageResponse
        | AIMessageResponse
    ]


class SlicedMessageListResponse(BaseModel):
    """
    슬라이싱된 메시지 리스트를 전달하기 위한 DTO
    """

    message_list: list[
        BaseMessageResponse
        | SystemMessageResponse
        | HumanMessageResponse
        | AIMessageResponse
    ]
    next_start_offset: int | None

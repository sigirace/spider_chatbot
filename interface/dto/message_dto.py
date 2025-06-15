from typing import Annotated, Literal
from datetime import datetime

from pydantic import BaseModel, Field
from fastapi import Query


from domain.messages.models.identifiers import MessageId
from domain.plans.plan import PlanInfo


class MessagesRequestBody(BaseModel):
    user_query: Annotated[str, Query(max_length=10240)]
    tts_required: Annotated[bool, Query(default=False)]


class AudioRequestBody(BaseModel):
    audio_data: Annotated[str, ...] = Field(description="음성 데이터 경로")


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

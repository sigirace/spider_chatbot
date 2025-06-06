from typing import Annotated, Literal, Union
from datetime import UTC, datetime

import langchain_core.messages
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import TypeAdapter

from domain.chats.models.identifiers import ChatId

from domain.messages.models.identifiers import MessageId
from domain.plans.plan import PlanInfo


class BaseMessage(BaseModel):
    model_config = ConfigDict(discriminator="role")  # type: ignore
    id: Annotated[MessageId | None, Field(max_length=100)] = Field(
        default=None, alias="_id", description="메시지의 식별자"
    )
    chat_id: Annotated[ChatId, Field(max_length=100)] = Field(
        description="메시지가 소속된 채팅의 식별자"
    )
    role: Literal["system", "user", "assistant"]
    content: Annotated[str | None, Field()] = Field(
        default=None, description="메시지의 내용"
    )
    metadata: Annotated[dict[str, str], ...] = Field(default={})

    @field_validator("metadata", mode="before")
    @classmethod
    def default_empty_metadata(cls, v):
        return v or {}

    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))

    def to_langchain_message(self):
        """
        Message 를 프롬프트에 사용하기 위해 Langchain 의 ChatMessage 계열 타입으로 변경하는 함수.
        채팅 관리를 위해 사용되는 필드들을 제외한 내용들로 구성된다.
        """
        content = self.content if self.content else ""
        metadata = self.metadata if self.metadata else None

        match self.role:
            case "system":
                return langchain_core.messages.SystemMessage(
                    content=content, metadata=metadata
                )
            case "user":
                return langchain_core.messages.HumanMessage(
                    content=content, metadata=metadata
                )
            case "assistant":
                return langchain_core.messages.AIMessage(
                    content=content, metadata=metadata
                )


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system"  # type: ignore


class HumanMessage(BaseMessage):
    role: Literal["user"] = "user"  # type: ignore

    def get_content(self):
        """
        content_formal: 단어가 정제된 질의문:
        """
        return self.metadata.get("content_formal", self.content)


class AIMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"  # type: ignore
    status: Annotated[
        Literal["pending", "progressing", "pause_for_input", "complete", "stalled"],
        Field(description="메시지의 처리 상태"),
    ] = Field(default="pending")
    plan: Annotated[PlanInfo | None, Field()] = Field(
        default=None, description="메시지의 처리 계획 및 도중의 결과"
    )


MessageUnion = Union[SystemMessage, HumanMessage, AIMessage]
MessageAdapter = TypeAdapter(MessageUnion)

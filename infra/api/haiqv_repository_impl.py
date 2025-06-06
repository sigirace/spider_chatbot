from typing import AsyncGenerator, Generator, List
from domain.api.exceptions import LlmServiceError
from domain.messages.models.message import BaseMessage
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama
from domain.api.llm_repository import ILlmRepository


class HaiqvRepositoryImpl(ILlmRepository):
    """HaiQV Chat Ollama 연동 구현"""

    def __init__(self, llm: HaiqvChatOllama):
        self.llm = llm

    def invoke(self, messages: List[BaseMessage]) -> str:
        try:
            return self.llm.invoke(messages)
        except Exception as e:
            raise LlmServiceError(str(e))

    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        try:
            return await self.llm.ainvoke(messages)
        except Exception as e:
            raise LlmServiceError(str(e))

    def stream(self, messages: List[BaseMessage]) -> Generator[str, None]:
        try:
            return self.llm.stream(messages)
        except Exception as e:
            raise LlmServiceError(str(e))

    async def astream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        try:
            return await self.llm.astream(messages)
        except Exception as e:
            raise LlmServiceError(str(e))

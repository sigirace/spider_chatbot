from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from domain.messages.models.message import BaseMessage


class ILlmRepository(ABC):
    """LLM 호출용 추상 인터페이스"""

    @abstractmethod
    async def invoke(self, messages: List[BaseMessage]) -> str:
        pass

    @abstractmethod
    async def ainvoke(self, messages: List[BaseMessage]) -> str:
        pass

    @abstractmethod
    async def stream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def astream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        pass

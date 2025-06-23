from abc import ABC, abstractmethod
from typing import AsyncGenerator

from domain.api.models import STTResponse


class IMLRepository(ABC):

    @abstractmethod
    async def stt(
        self,
        audio_encoding: str,
    ) -> STTResponse:
        pass

    @abstractmethod
    async def tts(
        self,
        text: str,
    ) -> AsyncGenerator[bytes, None]:
        pass

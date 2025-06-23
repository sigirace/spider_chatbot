from typing import AsyncGenerator
import httpx
from domain.api.ml_repository import IMLRepository
from config import get_settings
from domain.api.models import STTResponse

ml_settings = get_settings().ml


class MLRepositoryImpl(IMLRepository):
    def __init__(self):
        self.base_url = f"{ml_settings.ml_url}"

    async def stt(self, audio_encoding: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/stt",
                json={"waveform": audio_encoding},
            )
            response.raise_for_status()
            json_data = response.json()
            return STTResponse(**json_data)

    async def tts(self, text: str) -> AsyncGenerator[bytes, None]:
        timeout = httpx.Timeout(connect=10.0, read=None, write=10.0, pool=None)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                url=f"{self.base_url}/tts",
                json={
                    "text": text,
                    "voice_name": "af_heart",
                    "speed": 1,
                    "numpy": False,
                    "streaming": True,
                },
            ) as response:
                response.raise_for_status()

                async for chunk in response.aiter_bytes():
                    if not chunk:  # keep-alive 패킷 방지
                        continue
                    yield chunk  # bytes (raw)

import base64
from typing import Annotated

from pydantic import BaseModel, Field


class TokenChunk(BaseModel):
    v: Annotated[str, ...] = Field(
        default="", description="1개 이상의 메시지 토큰을 순서대로 이어붙인 문자열"
    )


class AudioChunk(BaseModel):
    a: Annotated[bytes, ...] = Field(default=b"", description="인코딩된 음성 토큰")

    @classmethod
    def from_bytes(cls, b: bytes) -> "AudioChunk":
        encoded = base64.b64encode(b).decode("utf-8")
        return cls(a=encoded)

from typing import Annotated

from pydantic import BaseModel, Field


class TokenChunk(BaseModel):
    v: Annotated[str, ...] = Field(
        default="", description="1개 이상의 메시지 토큰을 순서대로 이어붙인 문자열"
    )

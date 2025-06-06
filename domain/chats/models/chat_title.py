from typing import Annotated
from openai import BaseModel
from pydantic import Field


class TitleGenerateResult(BaseModel):
    """
    LLM 을 이용해 생성한 채팅 제목의 출력 형식
    """

    title: Annotated[str, Field(default="", description="생성된 채팅의 제목")]

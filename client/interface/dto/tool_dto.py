from typing import Optional, Any
from pydantic import BaseModel


class ParsedToolContent(BaseModel):
    """파싱된 1차 컨텐츠"""

    type: str
    text: str
    annotations: Optional[Any] = None


class ToolResponseData(BaseModel):
    """text 안에 담긴 실제 응답"""

    response: Any

from pydantic import BaseModel
from typing import Any


class ToolResult(BaseModel):
    response: Any

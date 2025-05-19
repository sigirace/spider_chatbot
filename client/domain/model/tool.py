from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    parameter_type: str = Field(..., alias="parameter_type")
    description: str
    required: bool = False
    default: Any = None


class ToolDef(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    metadata: Optional[Dict[str, Any]] = None
    identifier: str = ""


class ToolInvocationResult(BaseModel):
    content: str
    error_code: int

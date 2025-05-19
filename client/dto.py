from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    response: Any


class ToolParameter(BaseModel):
    """Represents a parameter for a tool.

    Attributes:
        name: Parameter name
        parameter_type: Parameter type (e.g., "string", "number")
        description: Parameter description
        required: Whether the parameter is required
        default: Default value for the parameter
    """

    name: str
    parameter_type: str = Field(..., alias="parameter_type")
    description: str
    required: bool = False
    default: Any = None


class ToolDef(BaseModel):
    """Represents a tool definition.

    Attributes:
        name: Tool name
        description: Tool description
        parameters: List of ToolParameter objects
        metadata: Optional dictionary of additional metadata
        identifier: Tool identifier (defaults to name)
    """

    name: str
    description: str
    parameters: List[ToolParameter]
    metadata: Optional[Dict[str, Any]] = None
    identifier: str = ""


class ToolInvocationResult(BaseModel):
    """Represents the result of a tool invocation.

    Attributes:
        content: Result content as a string
        error_code: Error code (0 for success, 1 for error)
    """

    content: str
    error_code: int

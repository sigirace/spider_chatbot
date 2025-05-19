"""
MCP SSE Client - A Python client for interacting with Model Context Protocol (MCP) endpoints.

This module provides a client for connecting to MCP endpoints using Server-Sent Events (SSE),
listing available tools, and invoking tools with parameters.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from mcp import ClientSession
from mcp.client.sse import sse_client
from pydantic import BaseModel

from client.dto import ToolDef, ToolInvocationResult, ToolParameter


class MCPClient:
    """Client for interacting with Model Context Protocol (MCP) endpoints"""

    def __init__(self, endpoint: str):
        """Initialize MCP client with endpoint URL

        Args:
            endpoint: The MCP endpoint URL (must be http or https)
        """
        if urlparse(endpoint).scheme not in ("http", "https"):
            raise ValueError(f"Endpoint {endpoint} is not a valid HTTP(S) URL")
        self.endpoint = endpoint

    async def list_tools(self) -> List[ToolDef]:
        """List available tools from the MCP endpoint

        Returns:
            List of ToolDef objects describing available tools
        """
        tools = []
        async with sse_client(self.endpoint) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                tools_result = await session.list_tools()

                for tool in tools_result.tools:
                    parameters = []
                    required_params = tool.inputSchema.get("required", [])
                    for param_name, param_schema in tool.inputSchema.get(
                        "properties", {}
                    ).items():
                        parameters.append(
                            ToolParameter(
                                name=param_name,
                                parameter_type=param_schema.get("type", "string"),
                                description=param_schema.get("description", ""),
                                required=param_name in required_params,
                                default=param_schema.get("default"),
                            )
                        )
                    tools.append(
                        ToolDef(
                            name=tool.name,
                            description=tool.description,
                            parameters=parameters,
                            metadata={"endpoint": self.endpoint},
                            identifier=tool.name,  # Using name as identifier
                        )
                    )
        return tools

    async def invoke_tool(
        self, tool_name: str, kwargs: Dict[str, Any], token: str
    ) -> ToolInvocationResult:
        """Invoke a specific tool with parameters

        Args:
            tool_name: Name of the tool to invoke
            kwargs: Dictionary of parameters to pass to the tool

        Returns:
            ToolInvocationResult containing the tool's response
        """
        async with sse_client(
            self.endpoint, headers={"Authorization": f"Bearer {token}"}
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, kwargs)

        return ToolInvocationResult(
            content="\n".join([result.model_dump_json() for result in result.content]),
            error_code=1 if result.isError else 0,
        )

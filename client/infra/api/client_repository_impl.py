from typing import Any, Dict, List
from urllib.parse import urlparse
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import (
    Tool,
    ListToolsResult,
    CallToolRequestParams,
    CallToolRequest,
    CallToolResult,
)
from client.domain.model.tool import ToolInvocationResult
from client.domain.repository.client_repository import IClientRepository


class ClientRepository(IClientRepository):
    def __init__(self, endpoint: str):
        if urlparse(endpoint).scheme not in ("http", "https"):
            raise ValueError(f"Endpoint {endpoint} is not a valid HTTP(S) URL")
        self.endpoint = endpoint

    def _tools_json_parser(self, tools_result: ListToolsResult) -> List[Tool]:
        return [tool.model_dump() for tool in tools_result.tools]

    async def list_tools(self) -> List[Tool]:
        async with sse_client(self.endpoint) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                tools_result = await session.list_tools()

                # tools_result가 Pydantic 모델일 경우 JSON 변환 → 다시 파싱
                parsed_tools = ListToolsResult(**tools_result.model_dump())

        return self._tools_json_parser(parsed_tools)

    async def invoke_tool(
        self, tool_name: str, kwargs: Dict[str, Any], token: str
    ) -> ToolInvocationResult:
        async with sse_client(
            self.endpoint, headers={"Authorization": f"Bearer {token}"}
        ) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, kwargs)

        return ToolInvocationResult(
            content="\n".join([r.model_dump_json() for r in result.content]),
            error_code=1 if result.isError else 0,
        )

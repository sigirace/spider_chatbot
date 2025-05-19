from typing import Any, Dict, List
from urllib.parse import urlparse
from mcp import ClientSession
from mcp.client.sse import sse_client

from client.domain.model.tool import ToolDef, ToolParameter, ToolInvocationResult
from client.domain.repository.client_repository import IClientRepository


class ClientRepository(IClientRepository):
    def __init__(self, endpoint: str):
        if urlparse(endpoint).scheme not in ("http", "https"):
            raise ValueError(f"Endpoint {endpoint} is not a valid HTTP(S) URL")
        self.endpoint = endpoint

    async def list_tools(self) -> List[ToolDef]:
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
                            identifier=tool.name,
                        )
                    )
        return tools

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

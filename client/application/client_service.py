from typing import List, Dict, Any
from client.domain.model.tool import ToolDef, ToolInvocationResult
from client.domain.repository.client_repository import IClientRepository


class ClientService:
    def __init__(self, repository: IClientRepository):
        self.repository = repository

    async def get_tool_list(self) -> List[ToolDef]:
        return await self.repository.list_tools()

    async def invoke_tool(
        self, tool_name: str, params: Dict[str, Any], token: str
    ) -> ToolInvocationResult:
        return await self.repository.invoke_tool(tool_name, params, token)

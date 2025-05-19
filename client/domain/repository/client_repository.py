from abc import ABC, abstractmethod
from typing import List, Dict, Any
from client.domain.model.tool import ToolDef, ToolInvocationResult


class IClientRepository(ABC):
    @abstractmethod
    async def list_tools(self) -> List[ToolDef]:
        pass

    @abstractmethod
    async def invoke_tool(
        self, tool_name: str, params: Dict[str, Any], token: str
    ) -> ToolInvocationResult:
        pass

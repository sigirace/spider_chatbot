from fastapi import APIRouter, Depends, Header, HTTPException
from typing import List, Dict, Any

from client.application.client_service import ClientService
from client.domain.model.tool import ToolDef, ToolInvocationResult
from dependency_injector.wiring import inject, Provide

from containers import Container
from users.domain.model.user import AuthUser
from users.interface.controller.user_depends import get_current_user

router = APIRouter(prefix="/mcp")

import json
from client.interface.dto.tool_dto import ParsedToolContent, ToolResponseData


def parse_tool_response(result: ToolInvocationResult) -> ToolResponseData:
    """ToolInvocationResult의 content를 파싱하여 ToolResponseData로 반환"""
    first = ParsedToolContent.parse_raw(result.content)  # 1차 JSON 파싱
    second = json.loads(first.text)  # 2차 파싱 (text 안에 있는 JSON)
    return ToolResponseData(**second)


@router.get("/tools", response_model=List[ToolDef])
@inject
async def get_tools(
    client_service: ClientService = Depends(Provide[Container.client_service]),
):
    return await client_service.get_tool_list()


@router.post("/tools/{tool_name}/invoke", response_model=ToolResponseData)
@inject
async def call_tool_parsed(
    tool_name: str,
    params: Dict[str, Any],
    user: AuthUser = Depends(get_current_user),
    client_service: ClientService = Depends(Provide[Container.client_service]),
):
    result = await client_service.invoke_tool(tool_name, params, user.access_token)
    return parse_tool_response(result)

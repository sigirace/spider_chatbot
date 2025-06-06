from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from application.prompts.create_prompt import CreatePrompt
from application.prompts.get_prompt import GetPrompt
from application.prompts.update_prompt import UpdatePrompt
from common.log_wrapper import log_request
from containers import Container

from domain.users.models import BaseUser
from interface.controller.dependency.auth import get_current_user
from interface.dto.prompt_dto import PromptCreateRequest, PromptUpdateRequest
from interface.mapper.prompt_mapper import PromptMapper


router = APIRouter(prefix="/prompts")


@router.post("")
@log_request()
@inject
async def create_prompt(
    request: PromptCreateRequest,
    create_prompt: CreatePrompt = Depends(Provide[Container.create_prompt]),
    user: BaseUser = Depends(get_current_user),
):
    prompt = PromptMapper.to_prompt(request, user.user_id)
    result = await create_prompt(prompt)

    return PromptMapper.to_prompt_create_response(result)


@router.get("/{prompt_name}")
@log_request()
@inject
async def get_prompt_by_name(
    prompt_name: str,
    get_prompt: GetPrompt = Depends(Provide[Container.get_prompt]),
):
    prompt = await get_prompt(prompt_name)

    return PromptMapper.to_prompt_create_response(prompt)


@router.put("/{prompt_name}")
@log_request()
@inject
async def update_prompt(
    prompt_name: str,
    prompt: PromptUpdateRequest,
    update_prompt: UpdatePrompt = Depends(Provide[Container.update_prompt]),
    user: BaseUser = Depends(get_current_user),
):
    prompt = PromptMapper.to_prompt_update_request(prompt, prompt_name)
    result = await update_prompt(prompt, user.user_id)

    return PromptMapper.to_prompt_create_response(result)

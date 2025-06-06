from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from containers import Container
from llms.application.ollama_service import OllamaService
from llms.domain.model.llm_schema import PromptRequest, PromptResponse
from llms.interface.dto.llm_dto import LlmRequest, LlmResponse
from users.domain.model.user import AuthUser, User
from users.interface.controller.user_depends import get_current_user
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/ollama")


@router.post("/chat")
@inject
async def chat(
    request: LlmRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
    user: AuthUser = Depends(get_current_user),
):
    # 인증된 사용자 정보 사용 가능
    print(f"[DEBUG] Authenticated user: {user.user_id}")
    prompt = PromptRequest(**request.model_dump())
    result: PromptResponse = ollama_service.chat(prompt)
    return LlmResponse(
        response=result.response,
    )


@router.post("/achat")
@inject
async def achat(
    request: LlmRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
    user: AuthUser = Depends(get_current_user),
):
    print(f"[DEBUG] Authenticated user: {user.user_id}")
    prompt = PromptRequest(**request.model_dump())
    result: PromptResponse = await ollama_service.chat_async(prompt)
    return LlmResponse(
        response=result.response,
    )


@router.post("/stream")
@inject
async def stream(
    request: LlmRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
    user: AuthUser = Depends(get_current_user),
):
    # 인증된 사용자 정보 사용 가능
    print(f"[DEBUG] Authenticated user: {user.user_id}")
    prompt = PromptRequest(**request.model_dump())
    result = ollama_service.chat_stream(prompt)
    return StreamingResponse(
        result,
        media_type="text/event-stream",
    )


@router.post("/astream")
@inject
async def astream(
    request: LlmRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
    user: AuthUser = Depends(get_current_user),
):
    print(f"[DEBUG] Authenticated user: {user.user_id}")
    prompt = PromptRequest(**request.model_dump())
    result = await ollama_service.chat_stream_async(prompt)
    return StreamingResponse(
        result,
        media_type="text/event-stream",
    )

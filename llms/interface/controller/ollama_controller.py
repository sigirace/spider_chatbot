from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from containers import Container
from llms.application.ollama_service import OllamaService
from llms.domain.ollama_schema import PromptRequest, PromptResponse
from llms.interface.dto.ollama_dto import OllamaRequest, OllamaResponse
from users.domain.model.user import User
from users.interface.controller.user_depends import get_current_user
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/llms")


@router.post("/chat")
@inject
async def chat(
    request: OllamaRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
    user: User = Depends(get_current_user),
):
    # 인증된 사용자 정보 사용 가능
    print(f"[DEBUG] Authenticated user: {user.user_id}")
    prompt = PromptRequest(**request.model_dump())
    result: PromptResponse = ollama_service.chat(prompt)
    return OllamaResponse(
        response=result.response,
    )


@router.post("/achat")
@inject
async def achat(
    request: OllamaRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
):
    prompt = PromptRequest(**request.model_dump())
    result: PromptResponse = await ollama_service.chat_async(prompt)
    return OllamaResponse(
        response=result.response,
    )


@router.post("/stream")
@inject
async def stream(
    request: OllamaRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
    user: User = Depends(get_current_user),
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
    request: OllamaRequest,
    ollama_service: OllamaService = Depends(Provide[Container.ollama_service]),
):
    prompt = PromptRequest(**request.model_dump())
    result = await ollama_service.chat_stream_async(prompt)
    return StreamingResponse(
        result,
        media_type="text/event-stream",
    )

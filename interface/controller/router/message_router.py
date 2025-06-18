from typing import Optional
from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from fastapi.responses import StreamingResponse
from application.messages.message_generator import MessageGenerator
from application.messages.message_list import MessageList
from application.service.stt_service import STTService
from common.log_wrapper import log_request
from containers import Container
from domain.chats.models.control import ControlSignal
from domain.chats.models.identifiers import ChatId
from domain.users.models import BaseUser
from interface.controller.dependency.auth import get_current_user
from interface.dto.message_dto import (
    AudioRequestBody,
    MessageListResponse,
    MessagesRequestBody,
    SlicedMessageListResponse,
)
from interface.dto.pagenation_dto import PagenationRequestParams
from interface.mapper.message_mapper import MessageMapper


router = APIRouter(prefix="/v2")


@router.get("/chats/{chat_id}/messages")
@log_request()
@inject
async def get_message_list(
    chat_id: ChatId,
    pagenation_params: PagenationRequestParams = Depends(PagenationRequestParams),
    user: BaseUser = Depends(get_current_user),
    message_list: MessageList = Depends(Provide[Container.message_list]),
):
    """
    messages GET: 채팅 세션에 해당하는 메시지들을 불러와 리턴

    현재 두 가지 모드(전체 질의, 페이지네이션 질의)로 제공하며 max_count
      1. 전체 질의: PagenationRequestParams 내 변수 중 max_count가 제공되지 않은 경우
      2. 페이지네이션 질의: PagenationRequestParams 내 변수 중 max_count 가 제공된 경우.
                       start_offset 은 Nullable 케이스 존재하므로 검증 제외

    전체 질의의 경우 현재 임시로 제공되는 질의 유형이며 이후 제외될 예정. 이때 이 API 로직 revise 필요
    """
    _message_list, next_start_offset = await message_list(
        chat_id=chat_id,
        user_id=user.user_id,
        pagenation_params=pagenation_params,
    )

    _dto_mapped_list = [MessageMapper.to_dto(message) for message in _message_list]

    if next_start_offset is None:
        response = MessageListResponse(
            message_list=_dto_mapped_list,
        )
    else:
        response = SlicedMessageListResponse(
            message_list=_dto_mapped_list,
            next_start_offset=next_start_offset,
        )

    return response


@router.post("/chats/{chat_id}/messages")
@log_request()
@inject
async def handle_message_request(
    chat_id: ChatId,
    request: MessagesRequestBody,
    user: BaseUser = Depends(get_current_user),
    message_generator: MessageGenerator = Depends(Provide[Container.message_generator]),
    app_id: Optional[str] = "ford",
):
    """
    유저 메시지를 채팅 세션의 마지막에 추가하고, 챗봇 동작을 시도
    """

    async def sse():
        try:
            async for chunk in message_generator(
                chat_id=chat_id,
                user_id=user.user_id,
                user_query=request.user_query,
                app_id=app_id,
                tts_required=request.tts_required,
            ):
                yield chunk
        except Exception as e:
            yield f"data: {ControlSignal(control_signal='error_occurred').model_dump_json()}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
    )


@router.post("/chats/{chat_id}/audio")
@log_request()
@inject
async def handle_audio_request(
    chat_id: ChatId,
    request: AudioRequestBody,
    user: BaseUser = Depends(get_current_user),
    message_generator: MessageGenerator = Depends(Provide[Container.message_generator]),
    stt_service: STTService = Depends(Provide[Container.stt_service]),
    app_id: Optional[str] = "ford",
):
    """
    유저 메시지를 채팅 세션의 마지막에 추가하고, 챗봇 동작을 시도
    STT 및 TTS 요청을 처리
    """

    ## 1. 음성 파일을 STT 서버로 전송

    ## 2. 전달받은 텍스트를 user_query로 사용

    async def sse():
        try:
            async for chunk in message_generator(
                chat_id=chat_id,
                user_id=user.user_id,
                user_query="test",
                app_id=app_id,
                tts_required=True,
            ):
                yield chunk
        except Exception as e:
            yield f"data: {ControlSignal(control_signal='error_occurred').model_dump_json()}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
    )

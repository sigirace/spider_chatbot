from datetime import UTC, datetime
from fastapi import APIRouter, Depends
from application.chats.create_chat import CreateChat
from application.chats.delete_chat import DeleteChat
from common.log_wrapper import log_request
from dependency_injector.wiring import Provide, inject

from application.chats.chat_list import ChatList
from containers import Container
from domain.chats.models.identifiers import ChatId
from domain.users.models import BaseUser
from interface.controller.dependency.auth import get_current_user
from interface.dto.chat_dto import ChatInfoListResponse, SlicedChatInfoListResponse
from interface.dto.common_dto import DeletedResponse
from interface.dto.pagenation_dto import PagenationRequestParams
from interface.mapper.chat_mapper import ChatInfoMapper

router = APIRouter(prefix="/chat")


@router.get("")
@log_request()
@inject
async def get_chat_list(
    user: BaseUser = Depends(get_current_user),
    pagenation_params: PagenationRequestParams = Depends(PagenationRequestParams),
    chat_list: ChatList = Depends(Provide[Container.chat_list]),
):
    """
    입력된 유저가 보유한 채팅 리스트를 출력
    """
    chat_info_list, next_start_offset = await chat_list(
        user_id=user.user_id,
        pagenation_params=pagenation_params,
    )

    _dto_mapped_list = [
        ChatInfoMapper.to_dto(chat_info) for chat_info in chat_info_list
    ]

    if next_start_offset is None:
        response = ChatInfoListResponse(chat_info_list=_dto_mapped_list)
    else:
        response = SlicedChatInfoListResponse(
            chat_info_list=_dto_mapped_list, next_start_offset=next_start_offset
        )

    return response


@router.post("")
@log_request()
@inject
async def new_chat(
    user: BaseUser = Depends(get_current_user),
    create_chat: CreateChat = Depends(Provide[Container.create_chat]),
):
    chat_info = await create_chat(user_id=user.user_id)

    return ChatInfoMapper.to_dto(
        chat_info=chat_info,
    )


@router.delete("/{chat_id}")
@log_request()
@inject
async def delete(
    chat_id: ChatId,
    user: BaseUser = Depends(get_current_user),
    delete_chat: DeleteChat = Depends(Provide[Container.delete_chat]),
):
    await delete_chat(chat_id=chat_id, user_id=user.user_id)

    return DeletedResponse(
        id=chat_id,
    )

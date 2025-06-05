from typing import List, Tuple
from common import handle_exceptions
from domain.chats.models.chat_info import ChatInfo
from domain.chats.repository.repository import IChatInfoRepository
from interface.dto.pagenation_dto import PagenationRequestParams


class ChatList:
    def __init__(
        self,
        chat_info_repository: IChatInfoRepository,
    ):
        self.chat_info_repository = chat_info_repository

    @handle_exceptions
    async def __call__(
        self,
        user_id: str,
        pagenation_params: PagenationRequestParams,
    ) -> Tuple[List[ChatInfo], int | None]:

        if pagenation_params.is_paginated():
            chat_info_list, next_start_offset = (
                await self.chat_info_repository.list_sliced(
                    owner_id=user_id,
                    start_offset=pagenation_params.start_offset,
                    max_count=pagenation_params.max_count,
                )
            )
        else:
            chat_info_list = await self.chat_info_repository.list_all_by_owner_id(
                owner_id=user_id,
                include_hidden=False,
            )
            next_start_offset = None

        return chat_info_list, next_start_offset

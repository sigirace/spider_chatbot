from typing import Any, List, Tuple

from application.service.validator import Validator
from common import handle_exceptions
from domain.chats.models.identifiers import ChatId
from domain.messages.models.message import BaseMessage
from domain.messages.repository.repository import IMessageRepository
from interface.dto.pagenation_dto import PagenationRequestParams


class MessageList:

    def __init__(
        self,
        message_repository: IMessageRepository,
        validator: Validator,
    ):
        self.message_repository = message_repository
        self.validator = validator

    @handle_exceptions
    async def __call__(
        self,
        chat_id: ChatId,
        user_id: str,
        pagenation_params: PagenationRequestParams,
    ) -> Tuple[List[BaseMessage], int | None]:

        chat_info = await self.validator.chat_validator(
            chat_id=chat_id, user_id=user_id
        )

        if pagenation_params.is_paginated():
            assert pagenation_params.max_count, "값 검증 오류"

            message_list, next_start_offset = await self.message_repository.list_sliced(
                chat_id=chat_id,
                start_offset=pagenation_params.start_offset,
                max_count=pagenation_params.max_count,
            )
        else:
            message_list = await self.message_repository.list_all_by_chat_id(
                chat_id=chat_info.id
            )
            next_start_offset = None

        return message_list, next_start_offset

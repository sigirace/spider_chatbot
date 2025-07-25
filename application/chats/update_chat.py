from application.service.validator import Validator
from common import handle_exceptions
from domain.chats.models.identifiers import ChatId
from domain.chats.repository.repository import IChatInfoRepository


class UpdateChat:

    def __init__(
        self,
        chat_info_repository: IChatInfoRepository,
        validator: Validator,
    ):
        self.chat_info_repository = chat_info_repository
        self.validator = validator

    @handle_exceptions
    async def __call__(
        self,
        chat_id: ChatId,
        user_id: str,
        primary_page: int,
    ):
        chat_info = await self.validator.chat_validator(
            chat_id=chat_id,
            user_id=user_id,
        )

        await self.chat_info_repository.update(
            chat_id=chat_info.id,
            primary_page=primary_page,
        )

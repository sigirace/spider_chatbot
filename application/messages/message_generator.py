from application.service.chat_service import ChatService
from application.service.validator import Validator
from domain.chats.models.identifiers import ChatId
from domain.messages.repository.repository import IMessageRepository


class MessageGenerator:

    def __init__(
        self,
        message_repository: IMessageRepository,
        validator: Validator,
        chat_service: ChatService,
    ):
        self.message_repository = message_repository
        self.validator = validator
        self.chat_service = chat_service

    async def __call__(
        self,
        chat_id: ChatId,
        user_id: str,
    ):
        chat_info = await self.validator.chat_validator(
            chat_id=chat_id,
            user_id=user_id,
        )

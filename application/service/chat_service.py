from typing import Generator
from domain.chats.models.chat_info import ChatInfo
from domain.chats.models.identifiers import ChatId
from domain.chats.repository.repository import IChatInfoRepository
from domain.messages.models.message import AIMessage, BaseMessage, HumanMessage
from domain.messages.repository.repository import IMessageRepository


class ChatService:
    def __init__(
        self,
        chat_info_repository: IChatInfoRepository,
        message_repository: IMessageRepository,
    ):
        self.chat_info_repository = chat_info_repository
        self.message_repository = message_repository

    async def determine_reusable(self, chat_info: ChatInfo) -> bool:
        """
        메시지가 하나도 없는 기존 채팅인지 확인
        """
        if chat_info.id is None:
            return False

        message_count = await self.message_repository.count_by_chat_id(
            chat_id=chat_info.id
        )

        return message_count == 0

    async def need_title_generation(self, chat_id: ChatId) -> bool:
        """
        제목 생성이 필요한지 확인
        """
        chat_info = await self.chat_info_repository.find_by_id(chat_id=chat_id)

        if chat_info.id is None:
            return False

        return chat_info.title is None

    async def get_message_history(
        self,
        chat_id: ChatId,
        max_count: int = 6,
    ):
        """
        private
        """
        return await self.message_repository.list_sliced(
            chat_id=chat_id,
            max_count=max_count,
        )

    async def save_user_message(
        self,
        chat_id: ChatId,
        message: str,
    ):
        user_message = HumanMessage(
            chat_id=chat_id,
            role="user",
            content=message,
        )
        user_message.id = await self.message_repository.insert(user_message)

        return user_message

    async def save_ai_message(
        self,
        chat_id: ChatId,
        status: str,
    ):
        assistant_message = AIMessage(
            chat_id=chat_id,
            role="assistant",
            status=status,
        )
        assistant_message.id = await self.message_repository.insert(assistant_message)

        return assistant_message

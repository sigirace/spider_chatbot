from application.service.chat_service import ChatService
from domain.chats.models.chat_info import ChatInfo
from domain.chats.repository.repository import IChatInfoRepository


class CreateChat:
    def __init__(
        self,
        chat_info_repository: IChatInfoRepository,
        chat_service: ChatService,
    ):
        self.chat_info_repository = chat_info_repository
        self.chat_service = chat_service

    async def __call__(self, user_id: str) -> ChatInfo:
        last_chat_info = await self.chat_info_repository.find_last_by_owner_id(
            owner_id=user_id,
            include_hidden=True,
        )

        if last_chat_info and await self.chat_service.determine_reusable(
            last_chat_info
        ):
            chat_info = ChatInfo(
                id=last_chat_info.id,
                owner_id=user_id,
            )
        else:
            chat_info = ChatInfo(
                owner_id=user_id,
            )

        chat_info.id = await self.chat_info_repository.save(chat_info=chat_info)
        return chat_info

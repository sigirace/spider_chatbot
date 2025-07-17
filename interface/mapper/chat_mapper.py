from domain.chats.models.chat_info import ChatInfo
from interface.dto.chat_dto import ChatInfoResponse


class ChatInfoMapper:
    @staticmethod
    def to_dto(chat_info: ChatInfo) -> ChatInfoResponse:
        assert chat_info.id
        assert chat_info.created_at

        dto = ChatInfoResponse(
            id=chat_info.id,
            owner_id=chat_info.owner_id,
            primary_page=chat_info.primary_page,
            title=chat_info.title,
            created_at=chat_info.created_at,
        )
        return dto

from domain.messages.models.message import AIMessage, BaseMessage
from interface.dto.message_dto import AIMessageResponse, BaseMessageResponse


class MessageMapper:
    @staticmethod
    def to_dto(message: BaseMessage) -> BaseMessageResponse:
        assert message.id
        assert message.created_at

        match message:
            case AIMessage():
                dto = AIMessageResponse(
                    id=message.id,
                    role=message.role,
                    status=message.status,
                    plan=message.plan,
                    content=message.content,
                    created_at=message.created_at,
                    metadata=message.metadata,
                )
            case _:
                """
                HumanMessage 및 SystemMessage 는 BaseMessage와 필드 및 처리가 동일하므로, 묶어서 처리.
                도메인과 DTO 에서는 미리 나눠두었음
                """
                dto = BaseMessageResponse(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                    metadata=message.metadata,
                )
        return dto

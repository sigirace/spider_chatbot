from bson import ObjectId
from pymongo import DESCENDING
from domain.chats.models.identifiers import ChatId
from domain.messages.models.identifiers import MessageId
from domain.messages.models.message import BaseMessage, MessageAdapter
from domain.messages.repository.repository import IMessageRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


COLLECTION_NAME = "message"


class MessageRepository(IMessageRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION_NAME]

    @staticmethod
    def serialize(message: BaseMessage) -> dict:
        dumped = message.model_dump(by_alias=True, exclude_none=True)
        dumped.update({"chat_id": ObjectId(message.chat_id)})
        if message.id:
            dumped.update({"_id": ObjectId(message.id)})
        return dumped

    @staticmethod
    def deserialize(document: dict) -> BaseMessage:
        return MessageAdapter.validate_python(
            document
            | {"_id": str(document["_id"]), "chat_id": str(document["chat_id"])}
        )

    async def list_all_by_chat_id(self, chat_id: ChatId) -> list[BaseMessage]:
        cursor = self.collection.find({"chat_id": ObjectId(chat_id)}).sort("_id", 1)
        messages = []
        async for doc in cursor:
            messages.append(self.deserialize(doc))
        return messages

    async def count_by_chat_id(self, chat_id: ChatId) -> int:
        return await self.collection.count_documents({"chat_id": ObjectId(chat_id)})

    async def list_sliced(
        self, chat_id: ChatId, max_count: int, start_offset: int | None = None
    ) -> tuple[list[BaseMessage], int | None]:
        message_count = await self.count_by_chat_id(chat_id=chat_id)

        if start_offset is None:
            start_offset = message_count

        skip_count = max(0, message_count - start_offset)

        cursor = (
            self.collection.find({"chat_id": ObjectId(chat_id)})
            .sort("_id", DESCENDING)
            .skip(skip_count)
            .limit(max_count)
        )

        sliced_docs = [doc async for doc in cursor]
        sliced_docs = list(reversed(sliced_docs))

        sliced_message_list = [self.deserialize(doc) for doc in sliced_docs]

        next_start_offset = min(start_offset, message_count) - len(sliced_message_list)

        non_terminal_condition = (
            next_start_offset > 0 and len(sliced_message_list) == max_count
        )
        terminal_condition = next_start_offset == 0
        assert (
            non_terminal_condition or terminal_condition
        ), "pagenation 처리 결과 검증에서 이상이 발견되었습니다. 로직 혹은 검증식을 확인하세요."

        return sliced_message_list, next_start_offset if next_start_offset > 0 else None

    async def insert(self, message: BaseMessage) -> MessageId:
        assert message.id is None, ValueError(
            "이미 ID가 부여된 메시지입니다. Message 를 중복으로 추가하려고 하는 것은 아닌지 점검하세요."
        )
        result = await self.collection.insert_one(self.serialize(message))
        return MessageId(result.inserted_id)

    async def update(self, message: BaseMessage) -> bool:
        assert message.id, ValueError(
            "ID가 부여되지 않은 메시지입니다. Message 객체의 id를 확인해주세요. id는 add_message 를 호출 시 부여됩니다."
        )
        object_id = ObjectId(message.id)
        result = await self.collection.update_one(
            {"_id": object_id},
            {"$set": self.serialize(message) | {"_id": object_id}},
        )
        return result.acknowledged

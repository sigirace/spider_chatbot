from bson import ObjectId
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from domain.chats.models.chat_info import ChatInfo
from domain.chats.models.identifiers import ChatId
from domain.chats.repository.repository import IChatInfoRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


COLLECTION_NAME = "chat_info"


class ChatInfoRepository(IChatInfoRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION_NAME]

    @staticmethod
    def serialize(chat_info: ChatInfo) -> dict:
        dumped = chat_info.model_dump(by_alias=True, exclude_none=True)
        if chat_info.id:
            dumped.update({"_id": ObjectId(chat_info.id)})
        return dumped

    @staticmethod
    def deserialize(document: dict) -> ChatInfo:
        return ChatInfo(**document | {"_id": str(document["_id"])})

    @staticmethod
    def make_find_query(
        owner_id: str, include_hidden: bool = False
    ) -> dict[str, str | bool]:
        query: dict[str, str | bool] = {"owner_id": owner_id}
        if not include_hidden:
            query["is_hidden"] = False
        return query

    async def find_by_id(self, chat_id: ChatId) -> ChatInfo | None:
        doc = await self.collection.find_one({"_id": ObjectId(chat_id)})
        return self.deserialize(doc) if doc else None

    async def is_chat_owner(self, chat_id: ChatId, owner_id: str) -> bool:
        count = await self.collection.count_documents(
            {"owner_id": owner_id, "_id": ObjectId(chat_id)}
        )
        return count > 0

    async def find_last_by_owner_id(
        self,
        owner_id: str,
        include_hidden: bool = False,
    ) -> ChatInfo | None:
        query = self.make_find_query(owner_id, include_hidden)
        doc = await self.collection.find_one(query, sort=[("_id", -1)])
        return self.deserialize(doc) if doc else None

    async def list_all_by_owner_id(
        self,
        owner_id: str,
        include_hidden: bool = False,
    ) -> list[ChatInfo]:
        query = self.make_find_query(owner_id, include_hidden)
        cursor = self.collection.find(query).sort([("_id", -1)])
        return [self.deserialize(doc) async for doc in cursor]

    async def count_by_owner_id(
        self,
        owner_id: str,
        include_hidden: bool = False,
    ) -> int:
        query = self.make_find_query(owner_id, include_hidden)
        return await self.collection.count_documents(query)

    async def list_sliced(
        self,
        owner_id: str,
        max_count: int,
        start_offset: int | None = None,
        include_hidden: bool = False,
    ) -> tuple[list[ChatInfo], int | None]:
        query = self.make_find_query(owner_id, include_hidden)
        chat_info_count = await self.count_by_owner_id(owner_id, include_hidden)

        if start_offset is None:
            start_offset = chat_info_count

        skip_count = max(0, chat_info_count - start_offset)

        cursor = (
            self.collection.find(query)
            .sort("_id", DESCENDING)
            .skip(skip_count)
            .limit(max_count)
        )

        sliced_docs = [doc async for doc in cursor]
        sliced_docs = list(reversed(sliced_docs))
        sliced_chat_info_list = [self.deserialize(doc) for doc in sliced_docs]

        next_start_offset = min(start_offset, chat_info_count) - len(
            sliced_chat_info_list
        )

        non_terminal_condition = (
            next_start_offset > 0 and len(sliced_chat_info_list) == max_count
        )
        terminal_condition = next_start_offset == 0
        assert (
            non_terminal_condition or terminal_condition
        ), "pagenation 처리 결과 검증에서 이상이 발견되었습니다. 로직 혹은 검증식을 확인하세요."

        return sliced_chat_info_list, (
            next_start_offset if next_start_offset > 0 else None
        )

    async def save(self, chat_info: ChatInfo) -> ChatId:
        if chat_info.id:
            await self.collection.update_one(
                {"_id": ObjectId(chat_info.id)},
                {"$set": self.serialize(chat_info)},
                upsert=True,
            )
            return chat_info.id
        else:
            result = await self.collection.insert_one(self.serialize(chat_info))
            return ChatId(result.inserted_id)

    async def soft_delete(self, chat_id: ChatId) -> bool:
        try:
            chat_info = await self.find_by_id(chat_id)
            assert chat_info
            chat_info.is_hidden = True
            await self.save(chat_info)
            return True
        except Exception:
            return False

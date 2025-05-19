from fastapi import HTTPException, status
from database.mongo import get_async_mongo_client
from users.domain.model.user import BaseUser, User
from users.domain.repository.user_repository import IUserRepository
from config import get_settings


CHAT_DB_CONFIG = get_settings().mongo
DB = CHAT_DB_CONFIG.mongodb_db


class UserRepository(IUserRepository):

    def __init__(self, collection: str = "user"):
        self.client = get_async_mongo_client()
        self.db = self.client[DB]
        self.collection = self.db[collection]

    async def get_by_user_id(self, user_id: str) -> User | None:
        user = await self.collection.find_one(
            {"user_id": user_id},
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User not found",
            )
        return User(**user)

    async def save(self, user: User) -> BaseUser:
        await self.collection.insert_one(user.model_dump())
        return BaseUser(
            user_id=user.user_id,
            user_name=user.user_name,
        )

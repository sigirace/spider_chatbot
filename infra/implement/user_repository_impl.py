from bson import ObjectId
from domain.users.models import UserCreate, User
from domain.users.repository import IUserRepository
from motor.motor_asyncio import AsyncIOMotorDatabase


COLLECTION_NAME = "user"


class UserRepositoryImpl(IUserRepository):

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION_NAME]

    async def get_by_user_id(self, user_id: str) -> User | None:

        d = await self.collection.find_one({"user_id": user_id})
        return User.model_validate(d) if d else None

    async def save(self, user: UserCreate) -> None:
        await self.collection.insert_one(
            user.model_dump(by_alias=True, exclude={"id"}),
        )

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from domain.prompts.models import Prompt
from domain.prompts.repository import IPromptRepository


COLLECTION_NAME = "prompt"


class PromptRepositoryImpl(IPromptRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[COLLECTION_NAME]

    async def create(
        self,
        prompt: Prompt,
    ) -> ObjectId:
        res = await self.collection.insert_one(
            prompt.model_dump(by_alias=True, exclude={"id"}),
        )
        return res.inserted_id

    async def get(
        self,
        prompt_id: ObjectId,
    ) -> Prompt | None:
        d = await self.collection.find_one({"_id": prompt_id})
        return Prompt.model_validate(d) if d else None

    async def get_by_name(
        self,
        name: str,
    ) -> Prompt | None:
        d = await self.collection.find_one({"name": name})
        return Prompt.model_validate(d) if d else None

    async def update(
        self,
        prompt_id: ObjectId,
        prompt: Prompt,
    ):
        await self.collection.replace_one(
            {"_id": prompt_id},
            prompt.model_dump(
                by_alias=True,
                exclude={"id"},
            ),
        )

    async def delete(
        self,
        prompt_id: ObjectId,
    ):
        await self.collection.delete_one({"_id": prompt_id})

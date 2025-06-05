from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION_NAME = "app"


async def indexes(db: AsyncIOMotorDatabase):
    await db[COLLECTION_NAME].create_index(
        [("creator", 1), ("app_name", 1)],
        unique=True,
        name="creator_app_unique",
    )
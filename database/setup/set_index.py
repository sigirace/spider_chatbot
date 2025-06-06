from motor.motor_asyncio import AsyncIOMotorDatabase

COLLECTION_NAME = "prompt"


async def indexes(db: AsyncIOMotorDatabase):
    await db[COLLECTION_NAME].create_index(
        [("name", 1)],
        unique=True,
        name="name_unique",
    )

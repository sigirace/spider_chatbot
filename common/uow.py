from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession


class MongoUnitOfWork:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._db = db
        self._client = db.client
        self._session: Optional[AsyncIOMotorClientSession] = None

    async def __aenter__(self) -> "MongoUnitOfWork":
        self._session = await self._client.start_session()
        self._session.start_transaction()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type:
                await self._session.abort_transaction()
            else:
                await self._session.commit_transaction()
        finally:
            await self._session.end_session()
            self._session = None

    @property
    def session(self) -> AsyncIOMotorClientSession:
        if self._session is None:
            raise RuntimeError("Session not active")
        return self._session

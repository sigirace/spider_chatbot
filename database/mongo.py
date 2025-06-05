from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import get_settings

CHAT_DB_CONFIG = get_settings().mongo

HOST = CHAT_DB_CONFIG.mongodb_host
PORT = CHAT_DB_CONFIG.mongodb_port
DB = CHAT_DB_CONFIG.mongodb_db
ID = CHAT_DB_CONFIG.mongodb_id
PW = CHAT_DB_CONFIG.mongodb_pw
CTS = CHAT_DB_CONFIG.connection_timeout_ms
STS = CHAT_DB_CONFIG.socket_timeout_ms
SSTS = CHAT_DB_CONFIG.server_selection_timeout_ms
QUERY_STRING = CHAT_DB_CONFIG.query_string


def get_async_mongo_client() -> AsyncIOMotorClient:
    MONGODB_URL = f"mongodb://{ID}:{PW}@{HOST}:{PORT}/?{QUERY_STRING}"
    return AsyncIOMotorClient(
        MONGODB_URL,
        connectTimeoutMS=CTS,
        socketTimeoutMS=STS,
        serverSelectionTimeoutMS=SSTS,
    )


def get_async_mongo_database(client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
    return client[DB]

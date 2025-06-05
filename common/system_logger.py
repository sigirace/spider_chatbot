import logging
import multiprocessing
import threading
from datetime import UTC, datetime

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import get_settings

MONGO = get_settings().mongo


class SystemLogger:
    LEVEL_MAP = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[MONGO.mongodb_log]
        self.stdout_logger = logging.getLogger("SystemLogger")
        if not self.stdout_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(filename)s:%(funcName)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.stdout_logger.addHandler(handler)
            self.stdout_logger.setLevel(logging.DEBUG)

    async def log(self, level: str, message: dict):
        now = datetime.now(UTC)
        level_number = self.LEVEL_MAP.get(level.upper(), 0)

        record = {
            "when": now.isoformat(),
            "levelName": level.upper(),
            "levelNumber": level_number,
            "fileName": message.get("fileName"),
            "functionName": message.get("functionName"),
            "processName": multiprocessing.current_process().name,
            "threadName": threading.current_thread().name,
            "user_id": message.get("user_id"),
            "trace_id": message.get("trace_id"),
            "state": message.get("state"),
            "detail": message.get("detail"),
            "args": message.get("args", {}),
        }

        self.stdout_logger.log(level_number, str(record))

        try:
            await self.collection.insert_one(record)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def info(self, message: dict):
        await self.log("INFO", message)

    async def error(self, message: dict):
        await self.log("ERROR", message)

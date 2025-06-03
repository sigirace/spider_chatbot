import logging
from log.log_handler import AsyncMongoLogHandler

mongo_handler = AsyncMongoLogHandler()
mongo_handler.setLevel(logging.INFO)


def get_mongo_handler():
    # 로그 핸들러 생성 (Mongo에 저장)
    return mongo_handler


def get_logger(name: str = "App Logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(mongo_handler)
    return logger

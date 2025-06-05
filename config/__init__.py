from functools import lru_cache

from config.haiqv_setting import HaiqvSetting
from config.jwt_setting import JWTSetting
from config.mongo_setting import MongoSetting
from config.milvus_setting import MilvusSetting


class Settings:
    def __init__(self):
        self.mongo = MongoSetting()
        self.jwt = JWTSetting()
        self.haiqv = HaiqvSetting()
        self.milvus = MilvusSetting()


@lru_cache()
def get_settings() -> Settings:
    return Settings()

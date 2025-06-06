from functools import lru_cache

from config.haiqv_setting import HaiqvSetting
from config.jwt_setting import JWTSetting
from config.mongo_setting import MongoSetting
from config.ollama_setting import OllamaSetting


class Settings:
    def __init__(self):
        self.mongo = MongoSetting()
        self.ollama = OllamaSetting()
        self.jwt = JWTSetting()
        self.haiqv = HaiqvSetting()


@lru_cache()
def get_settings() -> Settings:
    return Settings()

from config.setting import BaseAppSettings


class RerankSetting(BaseAppSettings):
    rerank_host: str
    rerank_port: str
    max_len: int

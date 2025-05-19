from config.setting import BaseAppSettings


class OllamaSetting(BaseAppSettings):
    ollama_host: str
    ollama_port: int
    ollama_model: str

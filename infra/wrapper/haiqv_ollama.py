from langchain_ollama import OllamaLLM
from config import get_settings

_settings = get_settings().haiqv


class HaiqvOllamaLLM(OllamaLLM):
    base_url: str = _settings.haiqv_url
    model: str = _settings.haiqv_model
    temperature: float = 0.0
    seed: int = 42

    # client_kwargs를 안전하게 초기화
    def model_post_init(self, __context) -> None:
        if self.client_kwargs is None:
            object.__setattr__(self, "client_kwargs", {})
        super().model_post_init(__context)

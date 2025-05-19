from typing import List, Generator, AsyncGenerator
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage
from config import get_settings

OLLAMA_CONFIG = get_settings().ollama


## 추상화 필요
class OllamaLLM:
    def __init__(self, model: str = OLLAMA_CONFIG.ollama_model):
        self.llm = ChatOllama(
            model=model,
            base_url=self.get_base_url(),
        )

    def get_base_url(self) -> str:
        return f"http://{OLLAMA_CONFIG.ollama_host}:{OLLAMA_CONFIG.ollama_port}"

    def chat(self, messages: List[BaseMessage]) -> str:
        return self.llm.invoke(messages).content

    async def chat_async(self, messages: List[BaseMessage]) -> str:
        response = await self.llm.ainvoke(messages)
        return response.content

    def chat_stream(self, messages: List[BaseMessage]) -> Generator[str, None, None]:
        for chunk in self.llm.stream(messages):
            yield chunk.content

    async def chat_stream_async(
        self, messages: List[BaseMessage]
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.llm.astream(messages):
            yield chunk.content

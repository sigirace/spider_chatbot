from typing import List, Generator, AsyncGenerator
from langchain_core.messages import BaseMessage
from llms.wrapper.haiqv_chat_ollama import HaiqvChatOllama


## 추상화 필요
class HaiqvLLM:
    def __init__(self):
        self.llm = HaiqvChatOllama()

    def chat(self, messages: List[BaseMessage]) -> str:
        return self.llm.invoke(messages).content

    async def chat_async(self, messages: List[BaseMessage]) -> str:
        response = await self.llm.ainvoke(messages)
        return response.content

    def chat_stream(self, messages: List[BaseMessage]) -> Generator[str, None, None]:
        for chunk in self.llm.stream(messages):
            yield f"data: {chunk.content}\n\n"

    async def chat_stream_async(
        self, messages: List[BaseMessage]
    ) -> AsyncGenerator[str, None]:
        async for chunk in self.llm.astream(messages):
            yield f"data: {chunk.content}\n\n"

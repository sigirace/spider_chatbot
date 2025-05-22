from typing import Generator, AsyncGenerator
from llms.infra.haiqv_api import HaiqvLLM
from llms.domain.model.llm_schema import PromptRequest, PromptResponse


class HaiqvService:
    def __init__(self, llm: HaiqvLLM):
        self.llm = llm

    def chat(self, request: PromptRequest) -> PromptResponse:
        human_message = request.to_human_message()
        reply = self.llm.chat([human_message])
        return PromptResponse(response=reply)

    def chat_stream(self, request: PromptRequest) -> Generator[str, None, None]:
        human_message = request.to_human_message()
        return self.llm.chat_stream([human_message])

    async def chat_async(self, request: PromptRequest) -> PromptResponse:
        human_message = request.to_human_message()
        reply = await self.llm.chat_async([human_message])
        return PromptResponse(response=reply)

    async def chat_stream_async(
        self, request: PromptRequest
    ) -> AsyncGenerator[str, None]:
        human_message = request.to_human_message()
        return self.llm.chat_stream_async([human_message])

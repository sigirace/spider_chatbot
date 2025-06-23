from typing import AsyncGenerator, List
from application.service.prompt_service import PromptService
from domain.api.ml_repository import IMLRepository
from domain.chats.models.token_chunk import AudioChunk
from domain.messages.models.message import BaseMessage
from domain.plans.plan import PlanInfo
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class TTSService:
    def __init__(
        self,
        ml_repository: IMLRepository,
        llm: HaiqvChatOllama,
        prompt_service: PromptService,
    ):
        self.ml_repository = ml_repository
        self.llm = llm
        self.prompt_service = prompt_service

    async def summary(
        self,
        chat_history: List[BaseMessage],
        user_query: str,
        plan: PlanInfo,
    ):
        system_prompt = await self.prompt_service.get_prompt("tts_summary")
        system_msg = SystemMessage(
            PromptTemplate(
                template=system_prompt, input_variables=["last_steps"]
            ).format(last_steps=str(plan.step_list))
        )

        tts_response = await self.llm.ainvoke(
            [
                *[m.to_langchain_message() for m in chat_history],
                system_msg,
                HumanMessage(content=user_query),
            ]
        )

        return tts_response.content.strip()

    async def convert(self, text: str) -> AsyncGenerator[bytes, None]:
        async for chunk in self.ml_repository.tts(text):
            yield AudioChunk.from_bytes(chunk).model_dump_json()

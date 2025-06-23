from typing import AsyncGenerator, List
from application.service.handler import HandlerService
from application.service.prompt_service import PromptService
from domain.chats.models.token_chunk import TokenChunk
from domain.messages.models.message import AIMessage, BaseMessage, HumanMessage
from domain.plans.plan import PlanInfo
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama
import langchain_core.messages
from langchain_core.prompts import PromptTemplate
from utils.async_utils import aenumerate


class GeneratorService:
    """Plan 완료 후 최종 답변 토큰 스트리머"""

    def __init__(
        self,
        handler: HandlerService,
        prompt_service: PromptService,
        llm: HaiqvChatOllama,
    ):
        self._handler = handler
        self._prompt_service = prompt_service
        self._llm = llm

    async def _token_stream(
        self,
        app_id: str,
        user_id: str,
        chat_history: List[BaseMessage],
        user_msg: HumanMessage,
        plan: PlanInfo,
        tts_summary: str | None = None,
    ):
        system_prompt = await self._prompt_service.get_prompt("final_answer_system")
        persona_prompt = await self._prompt_service.get_prompt("final_answer_persona")
        tool_description = await self._prompt_service.make_tool_prompt(
            app_id=app_id,
            user_id=user_id,
        )

        system_msg = langchain_core.messages.SystemMessage(
            PromptTemplate(
                template=system_prompt, input_variables=["last_steps", "tts_summary"]
            ).format(last_steps=str(plan.step_list), tts_summary=tts_summary)
        )

        messages = (
            [
                langchain_core.messages.SystemMessage(
                    persona_prompt.format(tool_description=tool_description)
                )
            ]  # persona
            + [m.to_langchain_message() for m in chat_history]
            + [system_msg]
            + [user_msg.to_langchain_message()]
        )

        # LangChain async stream
        async for chunk in self._llm.astream(messages):
            yield chunk

    async def stream_answer(
        self,
        app_id: str,
        user_id: str,
        chat_history: List[BaseMessage],
        user_msg: HumanMessage,
        assistant_msg: AIMessage,
        plan: PlanInfo,
        tts_summary: str | None = None,
        flush_every: int = 20,
    ) -> AsyncGenerator[TokenChunk, None]:
        buffer = ""
        async for idx, token in aenumerate(
            self._token_stream(
                app_id=app_id,
                user_id=user_id,
                chat_history=chat_history,
                user_msg=user_msg,
                plan=plan,
                tts_summary=tts_summary,
            ),
            1,
        ):
            tok_str = str(token.content or "")
            buffer += tok_str
            if idx % flush_every == 0:
                buffer = await self._handler.flush_content(assistant_msg, buffer)
            yield TokenChunk(v=tok_str).model_dump_json()

        if buffer:
            await self._handler.flush_content(assistant_msg, buffer)

        assistant_msg.status = "complete"
        await self._handler.message_repository.update(assistant_msg)

import asyncio
from typing import AsyncGenerator

from application.service.chat_service import ChatService
from application.service.executor import ExecutorService
from application.service.generator import GeneratorService
from application.service.handler import HandlerService
from application.service.planner import PlannerService
from application.service.stt_service import STTService
from application.service.title_service import TitleService
from application.service.tts_service import TTSService
from application.service.validator import Validator
from common import handle_exceptions
from domain.chats.models.identifiers import ChatId
from domain.plans.plan import PlanInfo
from domain.messages.models.message import AIMessage, HumanMessage


class MessageGenerator:
    """
    메인 플랜-실행-응답 토큰 스트림과
    비동기 제목 생성 스트림을 한 이벤트 루프에서 처리한다.
    """

    def __init__(
        self,
        validator: Validator,
        chat_service: ChatService,
        title_service: TitleService,
        planner: PlannerService,
        handler: HandlerService,
        executor: ExecutorService,
        generator: GeneratorService,
        tts_service: TTSService,
    ):
        self.validator = validator
        self.chat_service = chat_service
        self.title_service = title_service
        self.planner = planner
        self.handler = handler
        self.executor = executor
        self.generator = generator
        self.tts_service = tts_service

    @handle_exceptions
    async def __call__(
        self,
        *,
        chat_id: ChatId,
        user_id: str,
        user_query: str,
        app_id: str,
        tts_required: bool = False,
        flush_every: int = 20,
        verbose: bool = True,
    ) -> AsyncGenerator[str, None]:
        #  1. 유효성 검사
        await self.validator.chat_validator(chat_id=chat_id, user_id=user_id)

        #  2. 메시지 저장
        user_msg: HumanMessage = await self.chat_service.save_user_message(
            chat_id, user_query
        )
        assistant_msg: AIMessage = await self.chat_service.save_ai_message(
            chat_id, "progressing"
        )

        #  3. 히스토리 조회
        chat_history, _ = await self.chat_service.get_message_history(chat_id)

        #  4. 제목 생성 서브 태스크
        sub_queue: asyncio.Queue[str] = asyncio.Queue()
        title_task = None

        if await self.chat_service.need_title_generation(chat_id):

            async def _produce_title_signal() -> None:
                async for sig in self.title_service.generate_chat_title(
                    chat_id=chat_id,
                    user_message=user_msg,
                    verbose=verbose,
                ):
                    if sig:
                        await sub_queue.put(sig)

            title_task = asyncio.create_task(_produce_title_signal())

        #  5. Plan 초기 상태 emit
        plan = PlanInfo()
        await self.handler.persist_plan(assistant_msg, plan)
        yield f"data:{plan.model_dump_json(exclude_none=True)}\n\n"

        # processing 상태
        plan.status = "processing"
        await self.handler.persist_plan(assistant_msg, plan)
        yield f"data:{plan.model_dump_json(exclude_none=True)}\n\n"

        #  6. 플래너
        plan.step_list = await self.planner.create_plan(
            user_msg=user_msg,
            chat_history=chat_history,
            app_id=app_id,
            user_id=user_id,
            verbose=verbose,
        )
        await self.handler.persist_plan(assistant_msg, plan)
        yield f"data:{plan.model_dump_json(exclude_none=True)}\n\n"

        #  7. Executor (중간 Plan 상태 스트림)
        async for state in self.executor.execute_plan(
            plan=plan,
            chat_history=chat_history,
            user_msg=user_msg,
            app_id=app_id,
            user_id=user_id,
            verbose=verbose,
        ):
            await self.handler.persist_plan(assistant_msg, state)
            yield f"data:{state.model_dump_json(exclude_none=True)}\n\n"
            while not sub_queue.empty():  # 제목 신호 즉시 전달
                yield f"data:{await sub_queue.get()}\n\n"

        #  8. 음성 생성 서브 태스크
        tts_queue: asyncio.Queue[str] = asyncio.Queue()
        tts_task = None

        if tts_required:
            # 8.1 요약문 생성 - Invoke
            # 8.2 TTS 요청 - async
            pass

        #  9. Generator (최종 답변 토큰 스트림)
        async for token_json in self.generator.stream_answer(
            app_id=app_id,
            user_id=user_id,
            chat_history=chat_history,
            user_msg=user_msg,
            assistant_msg=assistant_msg,
            plan=plan,
            flush_every=flush_every,
        ):
            yield f"data:{token_json}\n\n"

            while not tts_queue.empty():  # 토큰 중에도 전달
                yield f"audio:{await tts_queue.get()}\n\n"

            while not sub_queue.empty():  # 토큰 중에도 전달
                yield f"data:{await sub_queue.get()}\n\n"

        assistant_msg.status = "complete"
        await self.handler.message_repository.update(assistant_msg)

        #  10. 음성 생성 서브 태스크 마무리
        if tts_task:
            await tts_task
            while not tts_queue.empty():
                yield f"audio:{await tts_queue.get()}\n\n"

        #  11. 제목 태스크 마무리
        if title_task:
            await title_task
            while not sub_queue.empty():
                yield f"data:{await sub_queue.get()}\n\n"

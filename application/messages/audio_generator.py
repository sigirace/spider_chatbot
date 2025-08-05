import asyncio
import json
from typing import AsyncGenerator, Optional

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
from domain.api.models import RerankOutput
from domain.chats.models.control import ControlSignal
from domain.chats.models.identifiers import ChatId
from domain.messages.models.message import AIMessage, HumanMessage
from domain.plans.plan import PlanInfo


class AudioGenerator:
    """
    음성 기반 채팅 응답 생성기
    STT -> 플래닝 -> 실행 -> LLM 답변 + TTS 를 스트리밍으로 처리
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
        stt_service: STTService,
        tts_service: TTSService,
    ):
        self.validator = validator
        self.chat_service = chat_service
        self.title_service = title_service
        self.planner = planner
        self.handler = handler
        self.executor = executor
        self.generator = generator
        self.stt_service = stt_service
        self.tts_service = tts_service

    @staticmethod
    def _extract_primary_page(signal_data: str) -> Optional[int]:
        """시그널 데이터에서 primary_page 값을 추출"""
        try:
            data = json.loads(signal_data)
            if data.get("control_signal") == "primary_page":
                return int(data.get("detail"))
        except (ValueError, TypeError, json.JSONDecodeError):
            pass
        return None

    @handle_exceptions
    async def __call__(
        self,
        *,
        chat_id: ChatId,
        user_id: str,
        user_query: str | None,
        audio_path: str | None,
        app_id: str,
        flush_every: int = 20,
        verbose: bool = True,
    ) -> AsyncGenerator[str, None]:
        # 1. 유효성 검사
        await self.validator.chat_validator(chat_id=chat_id, user_id=user_id)

        # 2. 음성 → 텍스트
        if user_query is None:
            stt_response = await self.stt_service.transcribe(audio_path)
            user_query = stt_response.text
            yield f"data:{ControlSignal(control_signal='stt_completed', detail=user_query).model_dump_json()}\n\n"

        # 3. 메시지 저장
        user_msg: HumanMessage = await self.chat_service.save_user_message(
            chat_id, user_query
        )
        assistant_msg: AIMessage = await self.chat_service.save_ai_message(
            chat_id, "progressing"
        )

        # 4. 히스토리 조회
        chat_history, _ = await self.chat_service.get_message_history(chat_id)

        # 5. 제목 생성 태스크
        sub_queue: asyncio.Queue = asyncio.Queue()
        title_task: Optional[asyncio.Task] = None

        if await self.chat_service.need_title_generation(chat_id):

            async def _produce_title_signal() -> None:
                async for sig in self.title_service.generate_chat_title(
                    chat_id=chat_id, user_message=user_msg, verbose=verbose
                ):
                    await sub_queue.put(("sub", sig))
                await sub_queue.put(("sub", None))

            title_task = asyncio.create_task(_produce_title_signal())

        # 6. Plan 초기화 및 상태 업데이트
        plan = PlanInfo()
        await self.handler.persist_plan(assistant_msg, plan)
        yield f"data:{plan.model_dump_json(exclude_none=True)}\n\n"

        plan.status = "processing"
        await self.handler.persist_plan(assistant_msg, plan)
        yield f"data:{plan.model_dump_json(exclude_none=True)}\n\n"

        # 7. 플래닝
        plan.step_list = await self.planner.create_plan(
            user_msg=user_msg,
            chat_history=chat_history,
            app_id=app_id,
            user_id=user_id,
            verbose=verbose,
        )
        await self.handler.persist_plan(assistant_msg, plan)
        yield f"data:{plan.model_dump_json(exclude_none=True)}\n\n"

        # 8. 플랜 실행
        signal_queue: asyncio.Queue = asyncio.Queue()
        primary_page_raw = None

        async for state in self.executor.execute_plan(
            plan=plan,
            chat_history=chat_history,
            user_msg=user_msg,
            app_id=app_id,
            user_id=user_id,
            signal_queue=signal_queue,
            verbose=verbose,
        ):
            await self.handler.persist_plan(assistant_msg, state)
            yield f"data:{state.model_dump_json(exclude_none=True)}\n\n"

            # 제목 시그널 즉시 전달
            while not sub_queue.empty():
                _, sig = await sub_queue.get()
                if sig:
                    yield f"data:{sig}\n\n"

        while not signal_queue.empty():
            primary_page_raw: list[RerankOutput] = await signal_queue.get()

        # primary page 업데이트
        if primary_page_raw is not None and len(primary_page_raw) > 0:
            try:
                pp = primary_page_raw[0].page

                if pp is not None:
                    await self.chat_service.update_primary_page(
                        chat_id=chat_id, primary_page=pp
                    )
                    assistant_msg.primary_page_list = primary_page_raw
                    yield f"data:{ControlSignal(control_signal='primary_page', detail=str(pp)).model_dump_json()}\n\n"

            except Exception as e:
                yield f"data:{ControlSignal(control_signal='error_occurred', detail=str(e)).model_dump_json()}\n\n"

        # 9. TTS 및 답변 생성
        output_queue: asyncio.Queue = asyncio.Queue()

        tts_summary = await self.tts_service.summary(
            chat_history=chat_history,
            user_query=user_query,
            plan=plan,
        )

        tts_ready = asyncio.Event()

        async def _produce_tts_signal() -> None:
            first = True
            async for sig in self.tts_service.convert(text=tts_summary):
                await output_queue.put(("tts", sig))
                if first:
                    tts_ready.set()
                    first = False
            await output_queue.put(("tts", None))

        async def _produce_gen_signal() -> None:
            async for token_json in self.generator.stream_answer(
                app_id=app_id,
                user_id=user_id,
                chat_history=chat_history,
                user_msg=user_msg,
                assistant_msg=assistant_msg,
                tts_summary=tts_summary,
                plan=plan,
                flush_every=flush_every,
            ):
                await output_queue.put(("gen", token_json))
            await output_queue.put(("gen", None))

        # 태스크 시작
        tts_task = asyncio.create_task(_produce_tts_signal())
        gen_task = asyncio.create_task(_produce_gen_signal())

        # 첫 오디오 청크 대기
        await tts_ready.wait()

        # 10. 스트림 출력
        gen_done = tts_done = False
        try:
            while not (gen_done and tts_done):
                src, payload = await output_queue.get()

                if payload is None:
                    if src == "gen":
                        gen_done = True
                    elif src == "tts":
                        tts_done = True
                    continue

                yield f"data:{payload}\n\n"

                # 제목 시그널 처리
                while not sub_queue.empty():
                    _, sig = await sub_queue.get()
                    if sig:
                        yield f"data:{sig}\n\n"

        finally:
            # 태스크 정리
            for task in (tts_task, gen_task, title_task):
                if task and not task.done():
                    task.cancel()
            await asyncio.gather(
                *(t for t in (tts_task, gen_task, title_task) if t),
                return_exceptions=True,
            )

            # 상태 업데이트
            assistant_msg.status = "complete"

            await self.handler.message_repository.update(assistant_msg)

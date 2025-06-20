import asyncio
import json
from typing import AsyncGenerator, List

from application.agents.retrieval import RetrievalAgent
from application.agents.summarization import SummarizationAgent
from application.agents.translation import TranslationAgent
from domain.messages.models.message import BaseMessage, HumanMessage
from domain.plans.plan import PlanInfo
from domain.plans.sub_step import SubStepInfo


class ExecutorService:
    def __init__(
        self,
        retrieval_agent: RetrievalAgent,
        summarization_agent: SummarizationAgent,
        translation_agent: TranslationAgent,
    ):
        self.retrieval_agent = retrieval_agent
        self.summarization_agent = summarization_agent
        self.translation_agent = translation_agent

    @staticmethod
    def _refresh_or_append(
        sub_step_list: List[SubStepInfo], new_info: SubStepInfo
    ) -> List[SubStepInfo]:
        sub_step_list = sub_step_list.copy()
        new_info = new_info.copy()

        if not sub_step_list:
            sub_step_list.append(new_info)
        elif sub_step_list[-1].status == "complete":
            sub_step_list.append(new_info)
        else:
            sub_step_list[-1] = new_info
        return sub_step_list

    async def _execute_single_step(
        self,
        idx: int,
        plan: PlanInfo,
        chat_history: List[BaseMessage],
        user_msg: HumanMessage,
        app_id: str,
        user_id: str,
        signal_queue: asyncio.Queue[str],
        verbose: bool,
    ) -> AsyncGenerator[PlanInfo, None]:
        step_info = plan.step_list[idx]
        step_info.status = "processing"
        yield plan

        current_query = user_msg.content or ""
        agent = step_info.agent.lower()

        # === Agent 선택 ===
        if agent == "translation":
            gen = self.translation_agent(
                current_user_query=current_query,
                chat_history=chat_history,
                step_list=plan.step_list,
                current_step_index=idx,
                verbose=verbose,
            )
        elif agent == "summarization":
            gen = self.summarization_agent(
                current_user_query=current_query,
                chat_history=chat_history,
                step_list=plan.step_list,
                current_step_index=idx,
                verbose=verbose,
            )
        elif agent == "retrieval":

            gen = self.retrieval_agent(
                user_id=user_id,
                app_id=app_id,
                user_query=current_query,
                queue=signal_queue,
            )
        else:
            step_info.status = "complete"
            yield plan
            return

        try:
            async for sub_info in gen:
                step_info.sub_step_list = self._refresh_or_append(
                    step_info.sub_step_list, sub_info
                )
                yield plan

            # 루프가 끝났으면 성공적으로 완료
            step_info.status = "complete"
            if step_info.sub_step_list:
                step_info.observation = step_info.sub_step_list[-1].observation
            yield plan

        except Exception as e:
            step_info.status = "stalled"
            if step_info.sub_step_list:
                step_info.sub_step_list[-1].status = "stalled"
            yield plan
            raise e

    async def execute_plan(
        self,
        plan: PlanInfo,
        chat_history: List[BaseMessage],
        user_msg: HumanMessage,
        app_id: str,
        user_id: str,
        signal_queue: asyncio.Queue[str],
        verbose: bool = True,
    ) -> AsyncGenerator[PlanInfo, None]:

        for idx, _ in enumerate(plan.step_list.root):
            async for state in self._execute_single_step(
                idx,
                plan,
                chat_history,
                user_msg,
                app_id,
                user_id,
                signal_queue,
                verbose,
            ):
                yield state
        plan.status = "complete"
        yield plan

import logging

from application.service.prompt_service import PromptService
from domain.plans.step import StepList
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama
from utils.str_utils import extract_json_array

logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d] %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

from typing import List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from domain.messages.models.message import BaseMessage, HumanMessage
import langchain_core.messages


class PlannerService:
    def __init__(self, prompt_service: PromptService):
        self._llm = HaiqvChatOllama()
        self._prompt_service = prompt_service
        self._step_parser = PydanticOutputParser(pydantic_object=StepList)

    async def create_plan(
        self,
        user_msg: HumanMessage,
        chat_history: List[BaseMessage],
        app_id: str,
        user_id: str,
        verbose: bool = True,
    ) -> StepList:
        if verbose:
            logger.info(f"[Planner] '{user_msg.content}' 에 대한 플랜 수립")

        system_prompt = await self._prompt_service.get_prompt("planner_system")

        tmpl = PromptTemplate(
            template=system_prompt,
            input_variables=[
                "user_msg",
                "chat_history",
                # "description",
                # "keywords",
            ],
        )

        prompt = tmpl.format(
            user_msg=user_msg.content,
            chat_history=(
                "This is the first query of the entire conversation flow."
                if len(chat_history) < 1
                else [m.to_langchain_message() for m in chat_history]
            ),
        )

        plan = await self._llm.ainvoke(
            [langchain_core.messages.AIMessage(content=prompt)]
        )
        plan_str = str(plan.content)
        cleaned_plan_str = extract_json_array(plan_str)

        if verbose:
            logger.info(f"[Planner] RAW LLM OUTPUT: {plan_str}")

        try:
            step_list = self._step_parser.parse(cleaned_plan_str)
        except Exception:
            logger.warning("Plan 파싱 실패 → 빈 리스트로 대체")
            step_list = self._step_parser.parse("[]")

        for step in step_list.root:
            step.agent = step.agent.lower()

        return step_list

import logging

from domain.plans.step import StepList

logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d] %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

from typing import List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_community.chat_models import AzureChatOpenAI
from domain.messages.models.message import BaseMessage
from domain.plans.plan import PlanInfo
import langchain_core.messages

_PROMPT_TEMPLATE = """You are a coordinator..."""


class PlannerService:
    def __init__(self, model: AzureChatOpenAI | None = None):
        self.model = model

    def create_plan(
        self,
        user_query: str,
        chat_history: List[BaseMessage],
        verbose: bool = True,
    ) -> PlanInfo:

        plan_prompt = PromptTemplate(
            template=_PROMPT_TEMPLATE,
            input_variables=["main_query", "chat_history"],
        ).format(
            main_query=user_query,
            chat_history=(
                "첫 대화"
                if not chat_history
                else [msg.to_langchain_message() for msg in chat_history]
            ),
        )

        plan_message = self.model.invoke(
            [langchain_core.messages.AIMessage(content=plan_prompt)]
        )
        plan_str = str(plan_message.content)

        if verbose:
            logging.info(f"Plan Str: {plan_str}")

        step_list_parser = PydanticOutputParser(pydantic_object=StepList)

        try:
            step_list = step_list_parser.parse(plan_str)
        except Exception as e:
            logging.warning(
                "수행 계획 파싱에 문제가 있었습니다. 플랜 없이 응답을 시도합니다."
            )
            step_list = step_list_parser.parse("[]")

        for step in step_list.root:
            step.agent = step.agent.lower()

        # 계획에 대한 로그
        if verbose:
            logging.info(f"Parsed Step List: {step_list}")

        return step_list

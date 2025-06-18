import logging
from typing import List

from domain.messages.models.message import BaseMessage
from domain.plans.observation_item import ObservationItem
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama

logger = logging.getLogger("summarization agent")
logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d] %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate

from domain.plans.step import StepList
from domain.plans.sub_step import SubStepInfo
from utils.prompt_utils import step_info_to_str, step_list_to_str


_SYSTAM_TEMPLATE = """
You are an agent responsible for performing summarization.  
Review the following conversation context, user query, and the overall processing plan, then generate a summary aligned with the intent of the current step.

Full execution plan for the user's query:  
{full_plan_string_for_query}

Intent of the current step that requires summarization:  
{current_step_string}

Guidelines:  
- Summarize only the parts that require summarization. Do not include unnecessary information.  
- The summary should be written in the **same language** as the original content being summarized.  
- After writing the summary result, end the response immediately.
"""


class SummarizationAgent:
    def __init__(self, llm: HaiqvChatOllama):
        self.llm = llm

    def build_message_list(
        self,
        current_user_query: str,
        chat_history: List[BaseMessage],
        step_list: StepList,
        current_step_index: int,
    ):

        # 프롬프트 구성
        system_prompt_template = PromptTemplate(
            template=_SYSTAM_TEMPLATE,
            input_variables=[
                "full_plan_string_for_query",
                "current_step_string",
            ],
        )

        system_prompt_str = system_prompt_template.format(
            main_query=current_user_query,
            full_plan_string_for_query=step_list_to_str(step_list),
            current_step_string=(
                step_info_to_str(step_list[current_step_index])
                if current_step_index
                else ""
            ),
        )
        message_list = (
            [m.to_langchain_message() for m in chat_history]
            + [HumanMessage(content=current_user_query)]
            + [SystemMessage(content=system_prompt_str)]
        )
        return message_list

    async def __call__(
        self,
        current_user_query: str,
        chat_history: List[BaseMessage],
        step_list: StepList,
        current_step_index: int,
        verbose: bool = False,
    ):
        """
        전체 맥락을 필요로 하는 에이전트.

        1. 메인 질의, 지난 채팅 히스토리, 현재의 스텝 리스트를 참조해서
        요약을 수행해야하며 이를 위한 프롬프트를 구성
        """
        sub_status = SubStepInfo(
            title="Generate a summary based on the current context."
        )
        if verbose:
            logging.info(f"{sub_status.title}")
        yield sub_status

        # Status 기록 및 출력
        sub_status.status = "processing"
        yield sub_status

        message_list = self.build_message_list(
            current_user_query=current_user_query,
            chat_history=chat_history,
            step_list=step_list,
            current_step_index=current_step_index,
        )
        # 요약 질의 수행
        model_response = await self.llm.ainvoke(input=message_list)

        summarized_text = model_response.content

        # Status 기록 및 출력
        sub_status.status = "complete"
        sub_status.observation = ObservationItem(type="string", value=summarized_text)
        yield sub_status

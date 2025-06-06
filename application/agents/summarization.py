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
당신은 요약을 수행하는 에이전트입니다.
다음 대화 내용, 사용자 질의 및 질의 처리 과정을 확인하고 현재 단계의 의도에 맞게 요약을 수행하세요.

사용자 질의에 대한 전체 수행 계획:
{full_plan_string_for_query}

당신이 요약을 수행해야 하는 현재 단계의 의도:
{current_step_string}

주의 사항:
- 요약이 필요한 부분만 정확하게 요약합니다. 불필요한 내용을 포함하지 않습니다.
- 요약 결과의 언어는 요약 대상 문자열의 언어와 동일한 언어로 작성해주세요.
- 요약 결과를 작성한 뒤에는 응답을 종료합니다.
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
        sub_status = SubStepInfo(title="현재 문맥에서의 요약문을 생성합니다.")
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

import logging
from typing import List

from domain.messages.models.message import BaseMessage
from domain.plans.observation_item import ObservationItem
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama
from utils.prompt_utils import step_info_to_str, step_list_to_str

logger = logging.getLogger("translation agent")
logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d] %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from langchain_core.messages import SystemMessage, HumanMessage
from domain.agents.translation import TranslationParameters
from domain.plans.step import StepList
from domain.plans.sub_step import SubStepInfo

_PROMPT_TEMPLATE_FOR_PARAMETERS_EXTRACTION = """\
You are a manager responsible for creating a "Translation Task Specification."  
Review the previous conversation and the current execution plan, and generate a task specification that includes the sentence to be translated and the target language.

Instructions:
- The task specification must be written in **JSON format** as follows:  
  {{ "string_to_translate": <<the full string that the translation agent should translate>>, "target_language": <<the target language for the translation>> }}
- The value of "target_language" must be written in **Korean**.
- After writing the task specification, end your response immediately.

Full execution plan for the most recent user query:  
{full_plan_string_for_query}

Current step within the execution plan for which you must write the task specification:  
{current_step_string}

Cautions:
- Refer to the full plan, but only write the specification for the **current step**.
- For the value of "string_to_translate", use the **exact sentence** that needs to be translated. You are **not** the translation agent. The actual translation will be performed by another agent based on this task specification.
"""


_SYSTEM_PROMPT_TEMPLATE_FOR_TRANSLATION = """\
You are a translation specialist agent responsible for translating user-provided sentences into {target_language}.  
Provide the translation result **only once**, based solely on the sentence given by the user.
"""


class TranslationAgent:
    def __init__(self, llm: HaiqvChatOllama):
        self.llm = llm

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

        1. 메인 질의, 지난 채팅 히스토리, 현재의 스텝 리스트를 이용해서
        1)번역을 실제로 수행할 부분과
        2)번역 대상 언어(패러미터가 될 것)를 지정하기 위한 프롬프트를 구성
        """
        sub_status = SubStepInfo(
            title="Extract the sentence to be translated and the target language based on the current context."
        )

        if verbose:
            logging.info(sub_status.title)
        yield sub_status

        # 1. 번역 체인에 사용할 패러미터 생성

        params_parser = PydanticOutputParser(pydantic_object=TranslationParameters)

        prompt_template = PromptTemplate(
            template=_PROMPT_TEMPLATE_FOR_PARAMETERS_EXTRACTION,
            input_variables=[
                "full_plan_string_for_query",
                "current_step_string",
            ],
            partial_variables={
                "format_instructions": params_parser.get_output_jsonschema()[
                    "properties"
                ]
            },
        )

        prompt_str = prompt_template.format(
            full_plan_string_for_query=step_list_to_str(step_list),
            current_step_string=(
                step_info_to_str(step_list[current_step_index])
                if current_step_index < len(step_list)
                else ""
            ),
        )

        model_response = await self.llm.ainvoke(
            [m.to_langchain_message() for m in chat_history]
            + [HumanMessage(content=current_user_query)]
            + [SystemMessage(content=prompt_str)]
        )
        agent_params = params_parser.parse(model_response.content)

        if verbose:
            logger.info(agent_params)

        sub_status.status = "complete"
        sub_status.observation = ObservationItem(
            type="key_value", value=agent_params.model_dump()
        )
        yield sub_status

        # 새 SubStep 상태 생성
        sub_status = SubStepInfo(
            title="Translate the extracted source sentence into the target language."
        )
        if verbose:
            logging.info(sub_status.title)
        yield sub_status

        # 진행중 상태 출력
        sub_status.status = "processing"
        yield sub_status

        translated_str = await self.translate(
            string_to_translate=agent_params.string_to_translate,
            target_language=agent_params.target_language,
            verbose=verbose,
        )

        # Status 기록 및 출력
        sub_status.status = "complete"
        sub_status.observation = ObservationItem(type="string", value=translated_str)
        yield sub_status

    async def translate(
        self,
        string_to_translate: str,
        target_language: str,
        **kwargs,
    ) -> str:

        # 번역 결과 생성을 위한 쿼리 메시지 구성
        prompt_template = PromptTemplate(
            template=_SYSTEM_PROMPT_TEMPLATE_FOR_TRANSLATION,
            input_variables=["target_language"],
        )
        prompt = prompt_template.format(target_language=target_language)

        model_response = await self.llm.ainvoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=string_to_translate),
            ]
        )

        return model_response.content

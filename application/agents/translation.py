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
당신은 "번역 작업의 명세서" 를 작성하는 매니저입니다.
지난 대화 내용 및 현재의 질의 처리 과정을 확인하고 번역 에이전트가 번역해야하는 대상 문장 및 번역 결과 언어를 작업 명세서로써 작성하세요.

작성 요령:
- 작업 명세서는 JSON 형식으로 작성하며, 형식은 다음과 같습니다.
{{"string_to_translate": <<언어 변환 에이전트가 번역할 전체 문자열 1개>>, "target_language": <<string_to_translate 가 번역될 타겟 언어>>}}
- target_language 의 값은 한국어로 작성해주세요.
- 작업 명세서를 작성한 뒤에는 응답을 종료합니다.

마지막 사용자 질의에 대한 수행 계획:
{full_plan_string_for_query}

당신이 작업 명세서를 작성해야 하는 전체 수행 계획 내 현재 단계:
{current_step_string}

주의 사항:
- 전체 수행 계획을 참고하여 현재의 단계에 대해서만 작성합니다.
- string_to_translate 의 값으로 번역이 필요한 문장을 "그대로" 작성 하세요. 당신은 번역 에이전트가 아닙니다. 번역 결과는 당신이 작성한 작업 명세서를 바탕으로 다른 에이전트가 수행할 예정입니다."""


_SYSTEM_PROMPT_TEMPLATE_FOR_TRANSLATION = """\
당신은 사용자가 말하는 문장을 {target_language}로 번역하는 번역 전문 에이전트입니다.
사용자가 제공하는 문장의 번역 결과만을 1회 작성하세요."""


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
            title="현재 문맥에서 번역 수행 대상과, 번역 대상 언어를 추출합니다."
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
            title="추출한 번역 수행 대상을 번역 대상 언어로 번역합니다"
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

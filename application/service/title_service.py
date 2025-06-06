import logging

from domain.chats.models.chat_title import TitleGenerateResult
from domain.chats.models.control import ControlSignal
from domain.chats.models.identifiers import ChatId
from domain.chats.repository.repository import IChatInfoRepository
from domain.chats.models.chat_info import ChatInfo
from langchain_core.output_parsers import PydanticOutputParser
import langchain_core.messages
from langchain_core.prompts import PromptTemplate
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama

logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s.%(msecs)03d] %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

from typing import AsyncGenerator
from domain.chats.models.chat_info import ChatInfo
from domain.chats.repository.repository import IChatInfoRepository
from domain.messages.models.message import HumanMessage


_CHAT_TITLE_SYSTEM_PROMPT = "당신은 대화 내용을 보고, 전체적인 주제를 잘 요약한 짧고 자연스러운 제목을 지어주는 도우미입니다. 간결하고 명확한 제목을 만들어주세요."
_USER_PROMPT_TEMPLATE_STR = """\
다음 글을 읽고, 글의 전체적인 주제를 잘 나타내는 간결한 제목을 한 문장으로 작성하시오. 너무 길거나 모호하지 않게 작성합니다.
글의 내용은 한화시스템ICT 임직원이 챗봇에게 질의한 질의문입니다.

1. 작성 요령
    - 응답은 반드시 json 모듈에 의해 즉시 parsing 가능한 json 형식으로 작성
        - 응답 json 은 title 이라는 단 하나의 key 만을 갖습니다
        - title 의 value 는 string 형식이며 질의문에 대한 제목을 의미합니다
    - 응답 예시: {{"title": "사무용 PC 교체 주기 문의"}}
    - 대화에 주제가 없는 경우 빈 json({{}}) 을 작성합니다.

2. 주의 사항
    - 불필요한 문자가 포함되지 않도록 주의합니다. 응답은 있는 그대로 json 해석기에 의해 해석될 예정입니다.
    - 질의문에 대해 응답을 작성하지 않도록 주의합니다.

질의문: {user_query}
"""


class TitleService:
    def __init__(
        self,
        chat_info_repository: IChatInfoRepository,
        llm: HaiqvChatOllama,
    ):
        self._chat_info_repository = chat_info_repository
        self._llm = llm

    async def generate_chat_title(
        self,
        chat_id: ChatId,
        user_message: HumanMessage,
        verbose: bool = True,
    ) -> AsyncGenerator[str, None]:

        chat_info = await self._chat_info_repository.find_by_id(chat_id=chat_id)

        if verbose:
            logging.info(
                f"채팅 {chat_info.id} 의 제목을 유추합니다: {user_message.content}"
            )

        user_prompt_template = PromptTemplate(
            template=_USER_PROMPT_TEMPLATE_STR, input_variables=["user_query"]
        )

        user_prompt = user_prompt_template.format(user_query=user_message.content)

        messages = [
            langchain_core.messages.SystemMessage(content=_CHAT_TITLE_SYSTEM_PROMPT),
            langchain_core.messages.HumanMessage(content=user_prompt),
        ]
        response = self._llm.invoke(messages)

        # 문자열로 출력된 타이틀 파싱
        title_parser = PydanticOutputParser(pydantic_object=TitleGenerateResult)

        generated_str = str(response.content)

        # 파싱 시도
        try:
            generated_title = title_parser.parse(generated_str).title
        except Exception as e:
            # 메시지 파싱에 실패한 케이스
            generated_title = None

        if generated_title is not None and generated_title != "":
            if verbose:
                logging.info(
                    f"채팅 {chat_info.id} 에 다음 채팅 제목이 생성되었습니다: {generated_title}"
                )

            chat_info.title = generated_title
            await self._chat_info_repository.save(chat_info=chat_info)

            yield ControlSignal(
                control_signal="title_generation_complete"
            ).model_dump_json()

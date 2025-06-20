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


_CHAT_TITLE_SYSTEM_PROMPT = "You are an assistant that creates short and natural-sounding titles summarizing the overall topic of a conversation. Please generate concise and clear titles."
_USER_PROMPT_TEMPLATE_STR = """\
Read the following message and generate a concise title that best represents the overall topic. The title should not be too long or vague.
The message is a question submitted by an employee of Hanwha Systems ICT to a chatbot.

1. Guidelines
    - The response must be in JSON format that can be immediately parsed by the json module
        - The JSON must contain only one key: "title"
        - The value of "title" must be a string representing the title of the question
    - Example: {{"title": "Inquiry about office PC replacement cycle"}}
    - If the message has no clear topic, return an empty JSON object: {{}}

2. Cautions
    - Ensure no unnecessary characters are included. The response will be parsed directly by a JSON parser.
    - Do not attempt to answer the question.

User message: {user_query}
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

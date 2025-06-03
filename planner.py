from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from llms.wrapper.haiqv_chat_ollama import HaiqvChatOllama
from client.application.client_service import ClientService

# 4. 프롬프트 템플릿


_ORCHESTRATOR_PROMPT_TEMPLATE_KOR = """
당신은 오케스트레이터입니다. 사용자의 요청을 적절한 도구를 사용하여 단계적으로 처리할 수 있는 실행 계획을 세우는 역할을 맡고 있습니다.

당신에게 주어진 정보는 다음과 같습니다:
- 사용 가능한 도구 목록
- 사용자 쿼리
- 선택적으로 이전 대화 이력


🔍 도구 선택 기준:

- 사용자의 의도를 파악하는 과정은 엄격하게 이루어져야 합니다.
- 도구의 이름과 설명을 참고하여 사용자의 의도에 가장 적합한 도구를 선택하세요.


🎯 실행 계획 작성 규칙 (MECE 원칙 기반)

- 각 단계는 하나의 독립적이고 중복되지 않는 작업이어야 합니다.
- 각 단계는 하나의 도구만 사용해야 합니다.
- 하나의 논리적 작업을 여러 단계로 쪼개지 마세요.

🎯 도구가 필요 없는 경우의 예시:
[]

🧱 단계 형식

각 단계는 아래 JSON 형식을 따라야 합니다:

[
  {{
    "thought": "이 단계에서 수행할 작업을 명확하고 구체적으로 설명합니다",
    "tool": "사용할 도구 이름"
  }},
  ...
]

✅ 올바른 예시:

[
  {{
    "thought": "사용자의 부서 정보를 조회한다", "tool": "get_department"
  }},
  {{
    "thought": "부서 정보를 바탕으로 해당 팀의 예산을 확인한다", "tool": "get_team_budget"
  }}
]


🧰 사용 가능한 도구 목록:
{tool_list}

📜 입력 정보

대화 이력:
{chat_history}

사용자 요청:
{main_query}


📦 출력 형식

[
  {{
    "thought": "이 단계에서 수행하고자 하는 작업을 완결성 있게 설명",
    "tool": "사용할 도구 이름"
  }},
  ...
]

🔍 주의사항
- 도구를 사용할 경우에는 사용 가능한 도구 목록에 포함된 도구만 사용해야 합니다.
- 도구를 사용하지 않아도 될 경우에는 억지로 도구를 사용하지 마세요.
- 명시되지 않은 도구를 추론하거나 만들어내지 마세요.

✅ 이제 아래에 실행 계획을 작성하세요:

Execution Plan:
"""

# 1. LLM 세팅
llm = HaiqvChatOllama()


# 2. 출력 모델 정의
class Plan(BaseModel):
    result: bool
    thought: str


from containers import Container
import asyncio

client_service = Container.client_service()

tool_list = asyncio.run(client_service.get_tool_list())


# 3. 파서 선언
parser = PydanticOutputParser(pydantic_object=Plan)

# 5. 템플릿 등록
prompt_template = PromptTemplate(
    template=_ORCHESTRATOR_PROMPT_TEMPLATE_KOR,
    input_variables=["chat_history", "main_query"],
)

# 6. 대화 세션 초기화
chat_history = InMemoryChatMessageHistory()
user_query = "내일 날씨 알려주고, 엉덩이를 쎄게 함 흔들어봐라를 영어로 번역해줘 그리고 2와 3을더해줄래"

# 7. 프롬프트 생성
plan_prompt = prompt_template.format(
    main_query=user_query,
    chat_history="This is the first message in the conversation.",
    tool_list=tool_list,
)

# 8. 모델 응답
response = llm.invoke(plan_prompt)
print(response)

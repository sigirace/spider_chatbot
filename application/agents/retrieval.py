import logging
from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from domain.api.models import RerankSchema, SearchResponse
from domain.api.rerank_repository import IRerankRepository
from domain.api.studio_repository import IStudioRepository
from domain.plans.observation_item import ObservationItem
from domain.plans.sub_step import SubStepInfo
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama

_KEYWORD_EXTRACTION_SYSTEM_PROMPT = """
사용자는 Query에 대해 문서 질의가 필요합니다.
Query와 가장 연관있는 문서를 찾기 위한 검색 문장을 출력 형식에 맞추어 정확히 {keyword_num_to_extract} 개만 작성하세요.


출력 형식:
{parser_instruction}

Query:
"""


class RetrievalAgent:
    def __init__(
        self,
        studio_repository: IStudioRepository,
        rerank_repository: IRerankRepository,
        llm: HaiqvChatOllama,
    ):
        self.studio_repository = studio_repository
        self.rerank_repository = rerank_repository
        self.llm = llm

    async def get_keyword_from_query(
        self,
        user_query: str,
        keyword_num_to_extract: int,
    ) -> List[str]:

        class KeywordsOfQuery(BaseModel):
            keyword_string_list: List[str] = Field(
                description="문서 질의에 사용할 키워드 문자열 리스트. 리스트 안에는 문자열만 포함되어야 하며, 정확히 "
                f"{keyword_num_to_extract}개 존재해야 합니다."
            )

        parser = PydanticOutputParser(pydantic_object=KeywordsOfQuery)

        messages = [
            SystemMessage(
                _KEYWORD_EXTRACTION_SYSTEM_PROMPT.format(
                    keyword_num_to_extract=keyword_num_to_extract,
                    parser_instruction=parser.get_format_instructions(),
                )
            ),
            HumanMessage(user_query),
        ]

        keyword_output = await self.llm.ainvoke(messages)
        keyword_parsed: KeywordsOfQuery = parser.invoke(keyword_output)
        keyword_string_list = keyword_parsed.keyword_string_list

        return keyword_string_list

    async def rerank_documents(
        self,
        documents: List[SearchResponse],
        query: str,
        top_n: int,
    ) -> List[SearchResponse]:
        rerank_schema = RerankSchema(
            documents=documents,
            query=query,
            top_n=top_n,
        )
        rerank_documents = await self.rerank_repository.compress_documents(
            rerank_schema
        )
        return rerank_documents

    def format_documents_to_strings(self, documents: List[SearchResponse]) -> List[str]:
        result: List[str] = []

        for doc in documents:
            parts = [doc.content.strip()]

            if doc.tags:
                tags_str = ", ".join(doc.tags)
                parts.append(f"주요태그: {tags_str}")

            parts.append(f"출처: {doc.document_name} - {doc.page} page")
            result.append("\n".join(parts))
        return result

    async def __call__(
        self,
        user_id: str,
        app_id: str,
        user_query: str,
        keyword_num_to_extract: int = 3,
        top_k: int = 3,
        top_n: int = 3,
        verbose: bool = False,
    ):

        sub_status = SubStepInfo(title="메인 질의문으로부터 키워드를 추출합니다")
        if verbose:
            logging.info(sub_status.title)
        yield sub_status

        sub_status.status = "processing"
        yield sub_status

        keyword_list = await self.get_keyword_from_query(
            user_query=user_query,
            keyword_num_to_extract=keyword_num_to_extract,
        )

        if verbose:
            logging.info(f"키워드 생성결과: {keyword_list}")

        # 키워드 생성 종료 출력
        sub_status.status = "complete"
        sub_status.observation = ObservationItem(type="keyword", value=keyword_list)
        yield sub_status

        # 여기서 유사도 검색 api 사용

        sub_status = SubStepInfo(title="추출한 키워드를 이용하여 문서를 검색합니다")
        yield sub_status

        sub_status.status = "processing"
        yield sub_status

        total_documents: List[SearchResponse] = []

        for keyword in keyword_list:
            similar_documents = await self.studio_repository.get_similar_documents(
                user_id=user_id,
                app_id=app_id,
                query=keyword,
                top_k=top_k,
            )
            total_documents.extend(similar_documents)

        unique_documents_dict = {doc.chunk_id: doc for doc in total_documents}
        unique_documents = list(unique_documents_dict.values())

        sub_status.status = "complete"
        yield sub_status

        sub_status = SubStepInfo(title="문서를 관련도 순으로 재정렬합니다")
        yield sub_status

        sub_status.status = "processing"
        yield sub_status

        rerank_documents = await self.rerank_documents(
            documents=unique_documents,
            query=user_query,
            top_n=top_n,
        )

        string_documents = self.format_documents_to_strings(rerank_documents)

        sub_status.status = "complete"
        sub_status.observation = ObservationItem(
            type="list",
            value=string_documents,
        )
        yield sub_status

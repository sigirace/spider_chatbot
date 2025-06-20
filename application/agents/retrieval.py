from asyncio import Queue
import json
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
The user needs to query the documents based on a given question.
Generate exactly {keyword_num_to_extract} search phrases that are most relevant to the query.
Follow the output format specified in {parser_instruction}.

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
                description=f"A list of keyword strings to be used for document retrieval. The list must contain only strings and must include exactly {keyword_num_to_extract} items."
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
                parts.append(f"primary tag: {tags_str}")

            parts.append(f"from: {doc.document_name} - {doc.page} page")
            result.append("\n".join(parts))
        return result

    async def __call__(
        self,
        user_id: str,
        app_id: str,
        user_query: str,
        queue: Queue[str],
        keyword_num_to_extract: int = 3,
        top_k: int = 3,
        top_n: int = 3,
        verbose: bool = False,
    ):

        sub_status = SubStepInfo(title="Extract keywords from the main query.")
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
            logging.info(f"keywords: {keyword_list}")

        # 키워드 생성 종료 출력
        sub_status.status = "complete"
        sub_status.observation = ObservationItem(type="keyword", value=keyword_list)
        yield sub_status

        # 여기서 유사도 검색 api 사용

        sub_status = SubStepInfo(title="Search documents using the extracted keywords.")
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
        if not unique_documents:
            sub_status.observation = ObservationItem(
                type="string",
                value="No relevant document in app.",
            )
            yield sub_status

            return

        yield sub_status

        sub_status = SubStepInfo(title="Re-rank the documents based on relevance.")
        yield sub_status

        sub_status.status = "processing"
        yield sub_status

        rerank_documents = await self.rerank_documents(
            documents=unique_documents,
            query=user_query,
            top_n=top_n,
        )
        await queue.put(
            json.dumps(
                {
                    "primary_page": rerank_documents[0].page,
                }
            )
        )

        string_documents = self.format_documents_to_strings(rerank_documents)

        sub_status.status = "complete"
        sub_status.observation = ObservationItem(
            type="list",
            value=string_documents,
        )
        yield sub_status

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from typing import Sequence


class AppInfo(BaseModel):
    description: str
    keywords: List[str]

    model_config = ConfigDict(extra="ignore")


class SearchResponse(BaseModel):
    chunk_id: str = Field(..., description="청크 ID")
    document_name: str = Field(..., description="문서 이름")
    page: int = Field(..., description="페이지 번호")
    content: str = Field(..., description="청크 내용")
    tags: List[str] = Field(default_factory=list, description="청크 태그")
    file_creation_date: str = Field(..., description="파일 생성 시간")
    file_modification_date: Optional[str] = Field(
        default=None, description="파일 수정 시간"
    )


class SearchResponseList(BaseModel):
    search_response_list: List[SearchResponse]


class RerankSchema(BaseModel):
    documents: Sequence[SearchResponse] = Field(..., description="문서 집합")
    query: str = Field(..., description="질의 내용")
    top_n: int = Field(..., description="반환할 문서 수")

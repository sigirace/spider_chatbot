import httpx
from typing import Sequence, List
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.callbacks import Callbacks
from fastapi import HTTPException
import numpy as np

from config import get_settings
from domain.api.models import RerankSchema, SearchResponse
from domain.api.rerank_repository import IRerankRepository

rerank = get_settings().rerank
MAX_LEN = rerank.max_len


def slice_by_len(text: str, limit: int = MAX_LEN) -> List[str]:
    """limit 길이 이하로 단순 슬라이스."""
    return [text[i : i + limit] for i in range(0, len(text), limit)] or [""]


class RerankRepositoryImpl(IRerankRepository, BaseDocumentCompressor):
    endpoint_url: str = f"http://{rerank.rerank_host}:{rerank.rerank_port}/rerank"

    async def compress_documents(
        self,
        rerank_schema: RerankSchema,
        callbacks: Callbacks | None = None,
    ) -> List[SearchResponse]:
        # 1) passage_list 및 매핑 구성
        passages: List[str] = []
        origin_map: List[int] = []
        for idx, doc in enumerate(rerank_schema.documents):
            for chunk in slice_by_len(doc.content):
                passages.append(chunk)
                origin_map.append(idx)

        payload = {
            "query": rerank_schema.query,
            "passage_list": passages,
        }

        # 2) HTTP 요청 (httpx 비동기 사용)
        try:
            async with httpx.AsyncClient(timeout=600, verify=False) as client:
                resp = await client.post(
                    self.endpoint_url,
                    json=payload,
                    headers={"accept": "application/json"},
                )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"ReRank 엔드포인트({self.endpoint_url}) 요청 실패: {e}",
            )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"ReRank 서버 오류: {resp.text}",
            )

        try:
            scores: List[float] = resp.json()["scores"]
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"ReRank 응답 파싱 실패: {e}, 응답 내용: {resp.text}",
            )

        if len(scores) != len(passages):
            raise HTTPException(
                status_code=500,
                detail="ReRank 응답 길이가 요청과 일치하지 않습니다.",
            )

        # 3) 문서별 최고 점수 집계
        doc_scores = np.full(len(rerank_schema.documents), -np.inf)
        for score, doc_idx in zip(scores, origin_map):
            doc_scores[doc_idx] = max(doc_scores[doc_idx], score)

        # 4) Top-N 선택
        top_n_idx = np.argsort(doc_scores)[::-1][: rerank_schema.top_n]
        return [rerank_schema.documents[i] for i in top_n_idx]

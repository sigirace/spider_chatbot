from abc import ABC, abstractmethod
from typing import List

from domain.api.models import RerankSchema, SearchResponse


class IRerankRepository(ABC):

    @abstractmethod
    async def compress_documents(
        self, rerank_schema: RerankSchema
    ) -> List[SearchResponse]:
        pass

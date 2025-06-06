from abc import ABC, abstractmethod
from typing import List

from domain.api.models import AppInfo, SearchResponse


class IStudioRepository(ABC):
    @abstractmethod
    async def get_app_info(self, user_id: str, app_id: str) -> AppInfo:
        pass

    @abstractmethod
    async def get_similar_documents(
        self,
        user_id: str,
        app_id: str,
        query: str,
        top_k: int,
    ) -> List[SearchResponse]:
        pass

from typing import List
import httpx
from domain.api.models import AppInfo, SearchResponse, SearchResponseList
from domain.api.studio_repository import IStudioRepository
from domain.api.exceptions import ExternalApiError
from config import get_settings
from infra.service.token_service import TokenService

studio_settings = get_settings().studio


class StudioRepositoryImpl(IStudioRepository):
    def __init__(self, token_service: TokenService):
        self.base_url = (
            f"http://{studio_settings.studio_host}:{studio_settings.studio_port}"
        )
        self.token_service = token_service

    def get_access_token(self, user_id: str) -> str:
        access_token, _ = self.token_service.publish_token(user_id)
        return access_token

    async def get_app_info(self, user_id: str, app_id: str) -> AppInfo:
        try:
            access_token = self.get_access_token(user_id)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/app/name/{app_id.upper()}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                json_data = response.json()
                return AppInfo(**json_data)
        except Exception as e:
            raise ExternalApiError(f"외부 API 호출 실패: {str(e)}")

    async def get_similar_documents(
        self,
        user_id: str,
        app_id: str,
        query: str,
        top_k: int,
    ) -> List[SearchResponse]:
        try:
            access_token = self.get_access_token(user_id)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embedding/search",
                    json={
                        "query": query,
                        "k": top_k,
                        "app_name": app_id.upper(),
                        "model_type": "kure",
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                json_data = response.json()

                search_response = SearchResponseList.model_validate(json_data)

                return search_response.search_response_list
        except Exception as e:
            raise ExternalApiError(f"외부 API 호출 실패: {str(e)}")

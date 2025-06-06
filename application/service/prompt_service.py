from typing import List
from domain.api.studio_repository import IStudioRepository
from domain.prompts.repository import IPromptRepository


class PromptService:
    def __init__(
        self,
        prompt_repository: IPromptRepository,
        studio_repository: IStudioRepository,
    ):
        self.prompt_repository = prompt_repository
        self.studio_repository = studio_repository

    async def get_prompt(self, prompt_name: str) -> str:
        prompt = await self.prompt_repository.get_by_name(prompt_name)
        return prompt.content

    async def make_tool_prompt(self, app_id: str, user_id: str) -> str:
        # app_id에 대한 정보를 가져와서 툴 프롬프트를 생성함
        tool_prompt = await self.get_prompt("tool_list")
        app_info = await self.studio_repository.get_app_info(
            user_id=user_id,
            app_id=app_id,
        )
        tool_prompt = tool_prompt.format(
            description=app_info.description,
            keywords=", ".join(app_info.keywords),
        )
        return tool_prompt

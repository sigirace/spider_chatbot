from common import handle_exceptions
from domain.prompts.models import Prompt
from domain.prompts.repository import IPromptRepository


class CreatePrompt:
    def __init__(self, prompt_repository: IPromptRepository):
        self.prompt_repository = prompt_repository

    @handle_exceptions
    async def __call__(self, prompt: Prompt) -> Prompt:

        prompt_id = await self.prompt_repository.create(prompt)
        prompt.id = prompt_id

        return prompt

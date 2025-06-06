from datetime import UTC, datetime
from application.service.validator import Validator
from common import handle_exceptions
from domain.prompts.models import BasePrompt, Prompt
from domain.prompts.repository import IPromptRepository


class UpdatePrompt:
    def __init__(self, prompt_repository: IPromptRepository, validator: Validator):
        self.prompt_repository = prompt_repository
        self.validator = validator

    @handle_exceptions
    async def __call__(self, prompt: BasePrompt, user_id: str) -> Prompt:

        existing_prompt = await self.validator.prompt_validator(prompt.name)

        existing_prompt.content = prompt.content
        existing_prompt.updater = user_id
        existing_prompt.updated_at = datetime.now(UTC)

        await self.prompt_repository.update(
            prompt_id=existing_prompt.id,
            prompt=existing_prompt,
        )

        return existing_prompt

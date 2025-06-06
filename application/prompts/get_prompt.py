from application.service.validator import Validator
from common import handle_exceptions
from domain.prompts.models import Prompt
from domain.prompts.repository import IPromptRepository


class GetPrompt:
    def __init__(self, validator: Validator):
        self.validator = validator

    @handle_exceptions
    async def __call__(self, prompt_name: str) -> Prompt | None:
        return await self.validator.prompt_validator(prompt_name)

from domain.prompts.models import BasePrompt, Prompt
from interface.dto.prompt_dto import (
    PromptCreateRequest,
    PromptCreateResponse,
    PromptUpdateRequest,
)


class PromptMapper:
    @staticmethod
    def to_prompt(request: PromptCreateRequest, user_id: str) -> Prompt:
        return Prompt(
            name=request.name,
            content=request.content,
            creator=user_id,
        )

    @staticmethod
    def to_prompt_create_response(prompt: Prompt) -> PromptCreateResponse:
        return PromptCreateResponse(
            id=str(prompt.id),
            name=prompt.name,
            content=prompt.content,
        )

    @staticmethod
    def to_prompt_update_request(
        request: PromptUpdateRequest, prompt_name: str
    ) -> BasePrompt:
        return BasePrompt(
            name=prompt_name,
            content=request.content,
        )

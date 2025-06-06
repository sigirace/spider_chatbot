from abc import ABC, abstractmethod

from bson import ObjectId
from domain.prompts.models import Prompt


class IPromptRepository(ABC):

    @abstractmethod
    async def create(self, prompt: Prompt) -> ObjectId:
        pass

    @abstractmethod
    async def get(self, prompt_id: ObjectId) -> Prompt | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Prompt | None:
        pass

    @abstractmethod
    async def update(self, prompt_id: ObjectId, prompt: Prompt) -> Prompt:
        pass

    @abstractmethod
    async def delete(self, prompt_id: ObjectId) -> None:
        pass

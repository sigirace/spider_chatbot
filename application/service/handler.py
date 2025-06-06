import logging

from domain.messages.models.message import AIMessage
from domain.messages.repository.repository import IMessageRepository
from domain.plans.plan import PlanInfo

logger = logging.getLogger(__name__)


class HandlerService:
    """PlanInfo·AssistantMessage 중간 저장 담당"""

    def __init__(self, message_repository: IMessageRepository):
        self.message_repository = message_repository

    async def persist_plan(self, assistant_msg: AIMessage, plan: PlanInfo) -> None:
        assistant_msg.plan = plan
        await self.message_repository.update(assistant_msg)

    async def flush_content(self, assistant_msg: AIMessage, buffer: str) -> str:
        if assistant_msg.content is None:
            assistant_msg.content = ""
        assistant_msg.content += buffer
        await self.message_repository.update(assistant_msg)
        return ""

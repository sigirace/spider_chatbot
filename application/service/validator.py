from fastapi import HTTPException, status
from domain.chats.models.identifiers import ChatId
from domain.chats.repository.repository import IChatInfoRepository
from domain.prompts.repository import IPromptRepository
from domain.users.models import User
from domain.users.repository import IUserRepository


class Validator:
    """
    유효성 검사를 위한 검증기
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        chat_info_repository: IChatInfoRepository,
        prompt_repository: IPromptRepository,
    ):
        self.user_repository = user_repository
        self.chat_info_repository = chat_info_repository
        self.prompt_repository = prompt_repository

    async def user_validator(
        self,
        user_id: str,
    ) -> User:

        user = await self.user_repository.get_by_user_id(user_id=user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found",
            )

        return user

    async def chat_validator(
        self,
        chat_id: ChatId,
        user_id: str,
    ):

        chat_info = await self.chat_info_repository.find_by_id(chat_id)

        if chat_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="채팅을 찾지 못했습니다.",
            )

        if chat_info.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다.",
            )

        return chat_info

    async def prompt_validator(
        self,
        prompt_name: str,
    ):
        prompt = await self.prompt_repository.get_by_name(prompt_name)

        if prompt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프롬프트를 찾지 못했습니다.",
            )

        return prompt

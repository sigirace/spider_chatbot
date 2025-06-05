from datetime import UTC, datetime
from fastapi import HTTPException, status
from common import handle_exceptions
from domain.users.models import BaseUser, UserCreate, User
from domain.users.repository import IUserRepository
from infra.service.crypto_service import CryptoService
from utils.object_utils import get_str_id


class SignUp:

    def __init__(
        self,
        user_repository: IUserRepository,
        crypto_service: CryptoService,
    ):
        self.user_repository = user_repository
        self.crypto_service = crypto_service

    @handle_exceptions
    async def __call__(
        self,
        user_req: UserCreate,
    ) -> BaseUser:
        user = await self.user_repository.get_by_user_id(
            user_id=user_req.user_id,
        )

        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User id already exists",
            )

        new_user = User(
            user_id=user_req.user_id,
            user_name=user_req.user_name,
            password=self.crypto_service.encrypt(user_req.password),
            created_at=datetime.now(UTC),
        )

        await self.user_repository.save(new_user)

        return BaseUser(
            user_id=user_req.user_id,
            user_name=user_req.user_name,
        )

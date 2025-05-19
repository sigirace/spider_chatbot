from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from users.domain.model.user import AuthUser, User
from users.domain.repository.user_repository import IUserRepository
from users.infra.repository.user_repository_impl import UserRepository
from utils.crypto import Crypto
from utils.jwt import (
    decode_token,
)

security = HTTPBearer()


class UserService:

    def __init__(self):
        self.user_repo: IUserRepository = UserRepository()
        self.crypto = Crypto()

    async def create_user(self, user_id: str, user_name: str, password: str) -> User:
        _user = None
        try:
            _user = await self.user_repo.get_by_user_id(user_id)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
            )

        now = datetime.now(timezone.utc)
        user: User = User(
            user_id=user_id,
            user_name=user_name,
            password=self.crypto.encrypt(password),
            created_at=now,
            updated_at=now,
        )
        await self.user_repo.save(user)
        return user

    async def login(self, user_id: str, password: str) -> User:
        user: User | None = await self.user_repo.get_by_user_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication",
            )
        if not self.crypto.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication",
            )
        return user

    async def get_user(self, token: str) -> AuthUser:
        try:
            payload = decode_token(token)
            user: User | None = await self.user_repo.get_by_user_id(payload["user_id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication, user not found",
                )
            return AuthUser(
                user_id=user.user_id,
                user_name=user.user_name,
                access_token=token,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication, token is invalid",
            )

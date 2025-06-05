from fastapi import HTTPException, status
from application.service.validator import Validator
from common import handle_exceptions
from domain.users.models import AuthToken, UserLogin
from domain.users.repository import IUserRepository
from infra.service.crypto_service import CryptoService
from infra.service.token_service import TokenService


class Login:
    def __init__(
        self,
        user_repository: IUserRepository,
        validator: Validator,
        token_service: TokenService,
        crypto_service: CryptoService,
    ):
        self.user_repository = user_repository
        self.validator = validator
        self.crypto_service = crypto_service
        self.token_service = token_service

    @handle_exceptions
    async def __call__(
        self,
        user_req: UserLogin,
    ) -> AuthToken:

        user = await self.validator.user_validator(user_id=user_req.user_id)

        if not self.crypto_service.verify(user_req.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비밀번호를 확인해주세요",
            )

        # token 발급
        access_token, refresh_token = self.token_service.publish_token(user.user_id)

        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
        )

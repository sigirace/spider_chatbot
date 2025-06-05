from domain.users.models import AuthToken, BaseUser, UserCreate, UserLogin
from interface.dto.user_dto import (
    TokenResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)


class UserMapper:

    @staticmethod
    def to_domain(request: UserCreateRequest) -> UserCreate:
        return UserCreate(
            user_id=request.user_id,
            user_name=request.user_name,
            password=request.password,
        )

    @staticmethod
    def to_response(user: BaseUser) -> UserResponse:
        return UserResponse(
            user_id=user.user_id,
            user_name=user.user_name,
        )

    @staticmethod
    def to_login_request(request: UserLoginRequest) -> UserLogin:
        return UserLogin(
            user_id=request.user_id,
            password=request.password,
        )

    @staticmethod
    def to_token_response(auth_token: AuthToken) -> TokenResponse:
        return TokenResponse(
            access_token=auth_token.access_token,
            refresh_token=auth_token.refresh_token,
        )

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from containers import Container
from users.application.token_service import TokenService
from users.application.user_service import UserService
from users.interface.dto.user_dto import (
    BaseUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)
from dependency_injector.wiring import Provide, inject


router = APIRouter(prefix="/users")


@router.post("/login", response_model=LoginResponse)
@inject
async def login(
    request: LoginRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
    token_service: TokenService = Depends(Provide[Container.token_service]),
) -> LoginResponse:
    try:
        user = await user_service.login(
            user_id=request.user_id,
            password=request.password,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    access_token = token_service.publish_token(user.user_id)

    return LoginResponse(
        access_token=access_token.access_token,
        refresh_token=access_token.refresh_token,
    )


@router.post("/signup", response_model=BaseUserResponse)
@inject
async def signup(
    request: RegisterRequest,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> BaseUserResponse:
    user = await user_service.create_user(
        user_id=request.user_id,
        user_name=request.user_name,
        password=request.password,
    )
    return BaseUserResponse(
        user_id=user.user_id,
        user_name=user.user_name,
    )

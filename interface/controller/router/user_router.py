from fastapi import APIRouter, Depends
from application.users.login import Login
from application.users.signup import SignUp
from common.log_wrapper import log_request
from dependency_injector.wiring import Provide, inject

from containers import Container
from domain.users.models import BaseUser
from interface.controller.dependency.auth import get_current_user
from interface.dto.user_dto import UserCreateRequest, UserLoginRequest
from interface.mapper.user_mapper import UserMapper

router = APIRouter(prefix="/user")


@router.post("/signup")
@log_request()
@inject
async def signup(
    request: UserCreateRequest,
    sign_up: SignUp = Depends(Provide[Container.signup]),
):
    create_requets = UserMapper.to_domain(request)
    user = await sign_up(create_requets)
    return UserMapper.to_response(user)


@router.post("/login")
@log_request()
@inject
async def login(
    request: UserLoginRequest,
    log_in: Login = Depends(Provide[Container.login]),
):
    login_request = UserMapper.to_login_request(request)
    auth_token = await log_in(login_request)
    return UserMapper.to_token_response(auth_token)


@router.get("/me")
@log_request()
@inject
async def me(
    user: BaseUser = Depends(get_current_user),
):
    return {
        "user_id": user.user_id,
        "user_name": user.user_name,
    }

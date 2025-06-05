from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.service.validator import Validator
from domain.users.models import BaseUser
from infra.service.token_service import TokenService
from containers import Container


security = HTTPBearer()


@inject
async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    token_service: TokenService = Depends(Provide[Container.token_service]),
    validator: Validator = Depends(Provide[Container.validator]),
) -> BaseUser:
    """
    - Authorization: Bearer <token>
    """
    decoded = token_service.validate_token(cred.credentials)

    _user = await validator.user_validator(decoded.get("user_id"))

    user = BaseUser.model_validate(_user)

    from middleware.request_context import get_request

    request = get_request()
    request.state.user = user

    return user

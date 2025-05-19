from fastapi import Depends
from dependency_injector.wiring import Provide, inject
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from containers import Container
from users.application.user_service import UserService
from users.domain.model.user import AuthUser

security = HTTPBearer()


@inject
async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> AuthUser:
    return await user_service.get_user(cred.credentials)

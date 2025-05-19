from dependency_injector import containers, providers

from users.application.token_service import TokenService
from users.application.user_service import UserService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        packages=[
            "users",
        ],
    )

    user_service = providers.Factory(
        UserService,
    )

    token_service = providers.Factory(
        TokenService,
    )

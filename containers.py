from dependency_injector import containers, providers

from client.application.client_service import ClientService
from client.infra.api.client_repository_impl import ClientRepository
from llms.application.haiqv_service import HaiqvService
from llms.application.ollama_service import OllamaService
from llms.infra.haiqv_api import HaiqvLLM
from llms.infra.ollama_api import OllamaLLM
from users.application.token_service import TokenService
from users.application.user_service import UserService


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
        packages=[
            "users",
            "llms",
            "client",
        ],
    )

    user_service = providers.Factory(
        UserService,
    )

    token_service = providers.Factory(
        TokenService,
    )

    ollama_llm = providers.Singleton(
        OllamaLLM,
    )

    ollama_service = providers.Factory(
        OllamaService,
        llm=ollama_llm,
    )

    haiqv_llm = providers.Singleton(
        HaiqvLLM,
    )

    haiqv_service = providers.Factory(
        HaiqvService,
        llm=haiqv_llm,
    )

    mcp_client = providers.Singleton(
        ClientRepository,
        endpoint="http://localhost:8001/sse",
    )

    client_service = providers.Factory(
        ClientService,
        repository=mcp_client,
    )

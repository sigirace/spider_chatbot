from dependency_injector import containers, providers

from application.chats.chat_list import ChatList
from application.chats.create_chat import CreateChat
from application.chats.delete_chat import DeleteChat
from application.messages.message_list import MessageList
from application.service.chat_service import ChatService
from application.service.validator import Validator
from application.users.login import Login
from application.users.signup import SignUp
from infra.implement.chat_repository_impl import ChatInfoRepository
from infra.implement.message_repository_impl import MessageRepository
from infra.implement.user_repository_impl import UserRepositoryImpl
from infra.service.crypto_service import CryptoService
from infra.service.token_service import TokenService
from common.system_logger import SystemLogger
from database.mongo import get_async_mongo_client, get_async_mongo_database
from infra.wrapper.haiqv_ollama import HaiqvOllamaLLM


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "interface.controller.dependency",
            "interface.controller.router",
            "middleware",
        ]
    )

    # database
    motor_client = providers.Singleton(get_async_mongo_client)
    motor_db = providers.Singleton(
        get_async_mongo_database,
        client=motor_client,
    )

    # logger
    system_logger = providers.Singleton(SystemLogger, db=motor_db)

    # api
    haiqv_ollama_llm = providers.Singleton(HaiqvOllamaLLM)

    # repository
    user_repository = providers.Factory(
        UserRepositoryImpl,
        db=motor_db,
    )
    chat_info_repository = providers.Factory(
        ChatInfoRepository,
        db=motor_db,
    )
    message_repository = providers.Factory(
        MessageRepository,
        db=motor_db,
    )

    # service
    token_service = providers.Factory(TokenService)
    crypto_service = providers.Factory(CryptoService)
    validator = providers.Factory(
        Validator,
        user_repository=user_repository,
        chat_info_repository=chat_info_repository,
    )
    chat_service = providers.Factory(
        ChatService,
        chat_info_repository=chat_info_repository,
        message_repository=message_repository,
    )

    # users
    signup = providers.Factory(
        SignUp,
        user_repository=user_repository,
        crypto_service=crypto_service,
    )
    login = providers.Factory(
        Login,
        user_repository=user_repository,
        validator=validator,
        token_service=token_service,
        crypto_service=crypto_service,
    )

    # chat
    chat_list = providers.Factory(
        ChatList,
        chat_info_repository=chat_info_repository,
    )
    create_chat = providers.Factory(
        CreateChat,
        chat_info_repository=chat_info_repository,
        chat_service=chat_service,
    )
    delete_chat = providers.Factory(
        DeleteChat,
        chat_info_repository=chat_info_repository,
        validator=validator,
    )

    # message
    message_list = providers.Factory(
        MessageList,
        message_repository=message_repository,
        validator=validator,
    )

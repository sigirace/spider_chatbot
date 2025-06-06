from dependency_injector import containers, providers

from application.agents.retrieval import RetrievalAgent
from application.agents.summarization import SummarizationAgent
from application.agents.translation import TranslationAgent
from application.chats.chat_list import ChatList
from application.chats.create_chat import CreateChat
from application.chats.delete_chat import DeleteChat
from application.messages.message_generator import MessageGenerator
from application.messages.message_list import MessageList
from application.prompts.create_prompt import CreatePrompt
from application.prompts.get_prompt import GetPrompt
from application.prompts.update_prompt import UpdatePrompt
from application.service.chat_service import ChatService
from application.service.executor import ExecutorService
from application.service.generator import GeneratorService
from application.service.handler import HandlerService
from application.service.planner import PlannerService
from application.service.prompt_service import PromptService
from application.service.title_service import TitleService
from application.service.validator import Validator
from application.users.login import Login
from application.users.signup import SignUp
from infra.api.rerank_repository_impl import RerankRepositoryImpl
from infra.api.studio_repository_impl import StudioRepositoryImpl
from infra.implement.chat_repository_impl import ChatInfoRepository
from infra.implement.message_repository_impl import MessageRepository
from infra.implement.prompt_repository_impl import PromptRepositoryImpl
from infra.implement.user_repository_impl import UserRepositoryImpl
from infra.service.crypto_service import CryptoService
from infra.service.token_service import TokenService
from common.system_logger import SystemLogger
from database.mongo import get_async_mongo_client, get_async_mongo_database
from infra.wrapper.haiqv_chat_ollama import HaiqvChatOllama


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
    haiqv_ollama_llm = providers.Singleton(HaiqvChatOllama)

    # base service
    token_service = providers.Factory(TokenService)
    crypto_service = providers.Factory(CryptoService)

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
    prompt_repository = providers.Factory(
        PromptRepositoryImpl,
        db=motor_db,
    )
    studio_repository = providers.Factory(
        StudioRepositoryImpl,
        token_service=token_service,
    )
    rerank_repository = providers.Factory(RerankRepositoryImpl)

    # agent
    retrieval_agent = providers.Factory(
        RetrievalAgent,
        studio_repository=studio_repository,
        rerank_repository=rerank_repository,
        llm=haiqv_ollama_llm,
    )
    summarization_agent = providers.Factory(
        SummarizationAgent,
        llm=haiqv_ollama_llm,
    )
    translation_agent = providers.Factory(
        TranslationAgent,
        llm=haiqv_ollama_llm,
    )

    # service
    validator = providers.Factory(
        Validator,
        user_repository=user_repository,
        chat_info_repository=chat_info_repository,
        prompt_repository=prompt_repository,
    )
    chat_service = providers.Factory(
        ChatService,
        chat_info_repository=chat_info_repository,
        message_repository=message_repository,
    )
    prompt_service = providers.Factory(
        PromptService,
        prompt_repository=prompt_repository,
        studio_repository=studio_repository,
    )
    handler = providers.Factory(
        HandlerService,
        message_repository=message_repository,
    )
    planner = providers.Factory(
        PlannerService,
        prompt_service=prompt_service,
    )
    executor = providers.Factory(
        ExecutorService,
        retrieval_agent=retrieval_agent,
        summarization_agent=summarization_agent,
        translation_agent=translation_agent,
    )
    generator = providers.Factory(
        GeneratorService,
        prompt_service=prompt_service,
        handler=handler,
        llm=haiqv_ollama_llm,
    )
    title_service = providers.Factory(
        TitleService,
        chat_info_repository=chat_info_repository,
        llm=haiqv_ollama_llm,
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
    message_generator = providers.Factory(
        MessageGenerator,
        validator=validator,
        chat_service=chat_service,
        title_service=title_service,
        planner=planner,
        handler=handler,
        executor=executor,
        generator=generator,
    )

    # prompt
    create_prompt = providers.Factory(
        CreatePrompt,
        prompt_repository=prompt_repository,
    )
    get_prompt = providers.Factory(
        GetPrompt,
        validator=validator,
    )
    update_prompt = providers.Factory(
        UpdatePrompt,
        prompt_repository=prompt_repository,
        validator=validator,
    )

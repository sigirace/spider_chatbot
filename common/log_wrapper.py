import functools
import inspect
import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import UploadFile

from common.system_logger import SystemLogger
from containers import Container
from middleware.request_context import get_request


def safe_serialize(obj):
    """UploadFile이나 기타 비직렬화 객체를 안전하게 문자열 또는 dict로 변환"""
    if isinstance(obj, UploadFile):
        return {
            "filename": obj.filename,
            "content_type": obj.content_type,
            "size": getattr(obj.file, "size", None),
        }
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [safe_serialize(v) for v in obj]
    return str(obj)


def log_request():
    def decorator(func):
        @functools.wraps(func)
        @inject
        async def wrapper(
            *args,
            logger: SystemLogger = Provide[Container.system_logger],
            **kwargs,
        ):
            request = get_request()
            trace_id = str(uuid.uuid4())
            request.state.request_id = trace_id

            user = getattr(request.state, "user", None)
            user_id = getattr(user, "user_id", "anonymous")

            frame = next(
                (
                    f
                    for f in inspect.stack()
                    if f.filename.endswith(".py") and "log_request" not in f.function
                ),
                inspect.stack()[2],
            )
            file_name = func.__module__.split(".")[-1] + ".py"
            function_name = func.__name__

            IGNORED_TYPES = (Provide,)

            filtered_kwargs = {
                k: safe_serialize(v)
                for k, v in kwargs.items()
                if (
                    k not in {"request", "user", "self"}
                    and not isinstance(v, IGNORED_TYPES)
                    and not repr(v).startswith("<dependency_injector.wiring.Provide")
                )
            }

            try:
                await logger.info(
                    {
                        "fileName": file_name,
                        "functionName": function_name,
                        "user_id": user_id,
                        "trace_id": trace_id,
                        "state": "START",
                        "detail": f"Executing {func.__name__}",
                        "args": filtered_kwargs,
                    }
                )

                result = await func(*args, **kwargs)

                await logger.info(
                    {
                        "fileName": file_name,
                        "functionName": function_name,
                        "user_id": user_id,
                        "trace_id": trace_id,
                        "state": "END",
                        "detail": f"Finished {func.__name__}",
                    }
                )
                return result

            except Exception as e:
                await logger.error(
                    {
                        "fileName": file_name,
                        "functionName": function_name,
                        "user_id": user_id,
                        "trace_id": trace_id,
                        "state": "EXCEPTION",
                        "detail": f"Failed: {str(e)}",
                    }
                )
                raise

        return wrapper

    return decorator

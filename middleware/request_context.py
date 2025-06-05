import contextvars

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_request_context_var: contextvars.ContextVar[Request] = contextvars.ContextVar(
    "request_context"
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = _request_context_var.set(request)
        try:
            response = await call_next(request)
            return response
        finally:
            _request_context_var.reset(token)


def get_request() -> Request:
    return _request_context_var.get()

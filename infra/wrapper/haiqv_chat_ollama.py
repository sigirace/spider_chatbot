from typing import Any
from langchain_ollama import ChatOllama
from config import get_settings

__all__ = ["HaiqvChatOllama"]


haiqv_setting = get_settings().haiqv


class HaiqvChatOllama(ChatOllama):
    """ChatOllama configured for the HaiQV proxy.

    Example
    -------
    >>> from haiqv_chat_ollama import HaiqvChatOllama
    >>> llm = HaiqvChatOllama(model="llama3", temperature=0)
    >>> print(llm.invoke([{"role": "user", "content": "Hello"}]).content)
    """

    # Change only the default – users can still override it
    base_url: str = haiqv_setting.haiqv_url
    model: str = haiqv_setting.haiqv_model

    # Optionally provide a friendlier alias so users don’t have to
    #      remember the long URL every time
    _HAIQV_BASE_URL: str = base_url  # for backwards-compat docs/examples

    # No __init__ override – let Pydantic handle construction

    # If you really want custom logic (e.g., inject client_kwargs)
    #     you can use `model_post_init` which runs *after* validation
    def model_post_init(self, __context: Any) -> None:  # noqa: N802
        # If the caller passed client_kwargs, keep them; otherwise ensure dict
        if self.client_kwargs is None:
            object.__setattr__(self, "client_kwargs", {})

        # You could tweak SSL verify, auth headers, etc. here, e.g.:
        # self.client_kwargs.setdefault("verify", False)  # ⚠️  example only

        # Call parent post-init to build HTTP clients
        super().model_post_init(__context)

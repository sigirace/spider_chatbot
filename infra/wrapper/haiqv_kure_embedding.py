from langchain_community.embeddings import OllamaEmbeddings
from config import get_settings

haiqv_setting = get_settings().haiqv

HAIQV_KURE_EMBEDDING_URL = haiqv_setting.haiqv_embed_kure_url
HAIQV_KURE_EMBEDDING_MODEL = haiqv_setting.haiqv_embed_kure_model

__all__ = ["HaiqvKureEmbedding"]


class HaiqvKureEmbedding(OllamaEmbeddings):
    """HaiQV kure-v1 embedding wrapper with configurable base_url and model.

    Example
    -------
    >>> embedder = HaiqvKureEmbedding(
    ...     base_url="https://ns-49-kure-v1.platform.haiqv.ai",
    ...     model="daynice/kure-v1"
    ... )
    >>> embedder.embed_query("오늘 날씨가 어떨까?")
    """

    base_url: str = HAIQV_KURE_EMBEDDING_URL
    model: str = HAIQV_KURE_EMBEDDING_MODEL

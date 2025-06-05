from typing import List
import requests
from langchain_core.embeddings import Embeddings

from config import get_settings

haiqv_setting = get_settings().haiqv

HAIQV_NOMIC_EMBEDDING_URL = haiqv_setting.haiqv_embed_nomic_url
HAIQV_NOMIC_EMBEDDING_MODEL = haiqv_setting.haiqv_embed_nomic_model


class HaiqvNomicEmbedding(Embeddings):
    """Custom embedding class for HTTP-based APIs like nomic v2."""

    base_url: str = HAIQV_NOMIC_EMBEDDING_URL
    model: str = HAIQV_NOMIC_EMBEDDING_MODEL

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {"model": self.model, "input": texts}
        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()

        return response.json()["data"]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]["embedding"]

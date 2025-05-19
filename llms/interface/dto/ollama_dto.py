from pydantic import BaseModel


class OllamaRequest(BaseModel):
    prompt: str


class OllamaResponse(BaseModel):
    response: str

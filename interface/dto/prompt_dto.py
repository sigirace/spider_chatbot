from pydantic import BaseModel


class PromptCreateRequest(BaseModel):
    name: str
    content: str


class PromptCreateResponse(BaseModel):
    id: str
    name: str
    content: str


class PromptUpdateRequest(BaseModel):
    content: str

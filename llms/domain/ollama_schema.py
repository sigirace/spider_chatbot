from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage


class PromptRequest(BaseModel):
    prompt: str

    def to_human_message(self) -> HumanMessage:
        return HumanMessage(content=self.prompt)


class PromptResponse(BaseModel):
    response: str

    @classmethod
    def from_ai_message(cls, message: AIMessage) -> "PromptResponse":
        return cls(response=message.content)

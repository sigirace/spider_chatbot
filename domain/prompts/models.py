from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from common.models import LifeCycle


class BasePrompt(BaseModel):
    name: str
    content: str


class Prompt(BasePrompt, LifeCycle):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    user_id: str
    user_name: str


class User(BaseUser):
    password: str
    created_at: datetime
    updated_at: Optional[datetime] = Field(default=None)


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str


class UserCreate(BaseModel):
    user_id: str
    user_name: str
    password: str


class UserLogin(BaseModel):
    user_id: str
    password: str

from datetime import datetime

from pydantic import BaseModel


class BaseUser(BaseModel):
    user_id: str
    user_name: str


class User(BaseUser):
    password: str
    created_at: datetime
    updated_at: datetime


class UserPayload(BaseUser):
    exp: datetime


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str


class CreateUserBody(BaseModel):
    user_id: str
    password: str

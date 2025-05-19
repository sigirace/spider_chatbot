from pydantic import BaseModel


class LoginRequest(BaseModel):
    user_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class BaseUserResponse(BaseModel):
    user_id: str
    user_name: str


class RegisterRequest(BaseModel):
    user_id: str
    user_name: str
    password: str

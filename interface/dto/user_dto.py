from pydantic import BaseModel


class BaseUserDTO(BaseModel):
    user_id: str
    user_name: str


class UserCreateRequest(BaseUserDTO):
    password: str


class UserLoginRequest(BaseModel):
    user_id: str
    password: str


class UserResponse(BaseUserDTO):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

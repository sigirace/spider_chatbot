from pydantic import BaseModel, Field


class BaseUserDTO(BaseModel):
    user_id: str
    user_name: str


class UserCreateRequest(BaseUserDTO):
    password: str


class UserLoginRequest(BaseModel):
    user_id: str = Field(..., alias="userId")
    password: str = Field(..., alias="password")


class UserResponse(BaseUserDTO):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginResponseData(BaseModel):
    clientIp: str
    empNo: str | None
    exp: str
    iat: str
    token: str
    userId: str


class LoginResponse(BaseModel):
    data: LoginResponseData

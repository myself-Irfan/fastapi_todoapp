from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.taskapp.task_schemas import ApiResponse


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description='User name')
    email: EmailStr
    password: str = Field(..., min_length=5)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5)


class UserOut(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class LoginTokenData(BaseModel):
    access_token: str
    refresh_token: str

class LoginResponse(ApiResponse):
    data: LoginTokenData


class RefreshTokenData(BaseModel):
    access_token: str

class RefreshTokenResponse(ApiResponse):
    data: RefreshTokenData


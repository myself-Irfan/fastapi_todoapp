from pydantic import BaseModel, Field


class LoginTokenData(BaseModel):
    access_token: str
    refresh_token: str

class RefreshTokenData(BaseModel):
    access_token: str

class RefreshTokenResponse(BaseModel):
    message: str = Field(..., description='Response message')

    data: RefreshTokenData
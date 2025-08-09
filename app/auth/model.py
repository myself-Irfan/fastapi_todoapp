from pydantic import BaseModel



class LoginTokenData(BaseModel):
    access_token: str
    refresh_token: str
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., title="Token string")
    token_type: str = Field(..., title="Token type")


class Auth(BaseModel):
    login: str = Field(..., title="Admin login")
    password: str = Field(..., title="Admin password")


class Admin(BaseModel):
    id: str = Field(..., title="Admin ID")
    login: str = Field(..., title="Admin login")

from pydantic import BaseModel

class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class UserLoginSchema(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

    token_type: str = 'bearer'


class RefreshTokenSchema(BaseModel):
    refresh_token: str
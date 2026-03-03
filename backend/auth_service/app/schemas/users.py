from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.roles import UserRole


class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str]
    skills: Optional[str]


class UserLoginSchema(BaseModel):
    email: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class UserReadSchema(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    phone: Optional[str]
    skills: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
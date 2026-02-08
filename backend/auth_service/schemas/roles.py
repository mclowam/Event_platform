from enum import Enum
from typing import Optional
from pydantic import BaseModel


class UserRole(str, Enum):
    USER = "user"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class UserPayload(BaseModel):
    user_id: int
    email: str
    role: str


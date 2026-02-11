from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class UserPayload(BaseModel):
    user_id: int
    email: str
    role: UserRole


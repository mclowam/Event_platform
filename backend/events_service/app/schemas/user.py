from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"
    ADMIN = "admin"

class UserPayload(BaseModel):
    user_id: int
    email: str
    role: str
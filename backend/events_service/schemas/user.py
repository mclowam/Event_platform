from pydantic import BaseModel


class UserPayload(BaseModel):
    user_id: int
    email: str
    role: str
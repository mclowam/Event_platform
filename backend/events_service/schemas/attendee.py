from datetime import datetime
from pydantic import BaseModel, ConfigDict
from schemas.event import EventResponseSchema

class ApplicationCreateSchema(BaseModel):
    event_id: int

class ApplicationResponseSchema(BaseModel):
    id: int
    user_id: int
    event_id: int
    applied_at: datetime
    event: EventResponseSchema

    model_config = ConfigDict(from_attributes=True)

class ApplicationStatusUpdateSchema(BaseModel):
    new_status: str
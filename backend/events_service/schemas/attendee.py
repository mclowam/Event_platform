from datetime import datetime

from pydantic import BaseModel, ConfigDict

from schemas.event import EventResponseSchema


class AttendeeResponseSchema(BaseModel):
    id: int
    events: EventResponseSchema
    user_id: int
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendeeSchema(BaseModel):
    event_id: int
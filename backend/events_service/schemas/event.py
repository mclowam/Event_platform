from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StatusResponseSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class EventResponseSchema(BaseModel):
    id: int
    title: str
    description: str
    organizer_id: int
    location: str
    status: StatusResponseSchema

    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventSchema(BaseModel):
    title: str
    description: str
    location: str
    status_id: int
    start_time: datetime
    end_time: datetime

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StatusResponseSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    title: str
    description: str
    location: str
    max_volunteers: int
    start_time: datetime
    end_time: datetime


class EventCreateSchema(EventBase):
    status_id: int


class EventUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    max_volunteers: Optional[int] = None
    status_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class EventResponseSchema(EventBase):
    id: int
    organizer_id: int
    status: StatusResponseSchema
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

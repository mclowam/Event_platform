from datetime import datetime
from typing import Optional

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
    image_url: Optional[str] = None

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
    image_url: Optional[str] = None

    start_time: datetime
    end_time: datetime


class EventUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    status_id: Optional[int] = None

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

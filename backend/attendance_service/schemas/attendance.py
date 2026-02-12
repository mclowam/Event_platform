from enum import Enum
from pydantic import BaseModel


class AttendanceStatus(str, Enum):
    REGISTERED = "registered"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    ABSENT = "absent"


class ManualAttendanceRequest(BaseModel):
    email: str
    event_id: int


class AttendanceStats(BaseModel):
    registered: int
    checked_in: int
    completed: int
    absent: int

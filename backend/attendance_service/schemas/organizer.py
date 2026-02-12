from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.attendance import AttendanceStatus


class ScanRequest(BaseModel):
    qr_token: str


class ScanResponse(BaseModel):
    status: str
    message: str

    volunteer_id: int
    event_id: int
    current_state: AttendanceStatus

    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    hours_worked: float = 0.0
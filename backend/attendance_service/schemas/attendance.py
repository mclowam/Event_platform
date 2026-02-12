from enum import Enum


class AttendanceStatus(str, Enum):
    REGISTERED = "registered"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    ABSENT = "absent"

from sqlalchemy import select

from db.session import SessionDep
from models.attendance import Attendance
from schemas.attendance import AttendanceStatus, AttendanceStats


async def stats_event(session: SessionDep, event_id: int):
    query_registered = select(Attendance).where(Attendance.status == AttendanceStatus.REGISTERED).where(Attendance.event_id == event_id)
    query_checked_in = select(Attendance).where(Attendance.status == AttendanceStatus.CHECKED_IN).where(Attendance.event_id == event_id)
    query_completed = select(Attendance).where(Attendance.status == AttendanceStatus.COMPLETED).where(Attendance.event_id == event_id)
    query = select(Attendance).where(Attendance.status == AttendanceStatus.ABSENT).where(Attendance.event_id == event_id)

    result_registered = (await session.execute(query_registered)).scalars().all()
    result_checked_in = (await session.execute(query_checked_in)).scalars().all()
    result_completed = (await session.execute(query_completed)).scalars().all()
    result_absent = (await session.execute(query)).scalars().all()

    return AttendanceStats(
        registered=len(result_registered),
        checked_in=len(result_checked_in),
        completed=len(result_completed),
        absent=len(result_absent),
    )
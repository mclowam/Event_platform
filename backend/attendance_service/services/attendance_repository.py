from sqlalchemy import select

from db.session import SessionDep
from models.attendance import Attendance
from schemas.attendance import AttendanceStatus


class AttendanceRepository:
    def __init__(self, session: SessionDep):
        self._session = session

    async def get_by_event_and_user(self, event_id: int, user_id: int) -> Attendance | None:
        query = select(Attendance).where(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, attendance: Attendance) -> Attendance:
        self._session.add(attendance)
        await self._session.commit()
        await self._session.refresh(attendance)
        return attendance

    async def update(self, attendance: Attendance) -> Attendance:
        await self._session.commit()
        await self._session.refresh(attendance)
        return attendance

    async def get_counts_by_event(self, event_id: int) -> dict:
        counts = {}
        for status in AttendanceStatus:
            query = select(Attendance).where(
                Attendance.event_id == event_id,
                Attendance.status == status,
            )
            result = await self._session.execute(query)
            counts[status] = len(result.scalars().all())
        return counts
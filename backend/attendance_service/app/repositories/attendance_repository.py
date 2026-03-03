from sqlalchemy import select

from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceStatus
from app.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository[Attendance]):
    model = Attendance

    async def get_by_event_and_user(self, event_id: int, user_id: int) -> Attendance | None:
        query = select(Attendance).where(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

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

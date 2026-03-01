from schemas.attendance import AttendanceStatus, AttendanceStats

from .abstractions import IAttendanceStatsRepository


class AttendanceStatsService:

    def __init__(self, stats_repository: IAttendanceStatsRepository) -> None:
        self._repo = stats_repository

    async def get_stats(self, event_id: int) -> AttendanceStats:
        counts = await self._repo.get_counts_by_event(event_id)
        return AttendanceStats(
            registered=counts.get(AttendanceStatus.REGISTERED, 0),
            checked_in=counts.get(AttendanceStatus.CHECKED_IN, 0),
            completed=counts.get(AttendanceStatus.COMPLETED, 0),
            absent=counts.get(AttendanceStatus.ABSENT, 0),
        )

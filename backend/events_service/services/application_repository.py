from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from db.session import SessionDep
from models import VolunteerApplication, Event
from schemas.attendee import ApplicationResponseSchema


class ApplicationRepository:
    def __init__(self, session: SessionDep):
        self._session = session

    async def my_applications(self, user_id: int) -> list:
        query = (
            select(VolunteerApplication)
            .where(VolunteerApplication.user_id == user_id)
            .options(
                selectinload(VolunteerApplication.event)
                .selectinload(Event.status)
            )
        )
        result = await self._session.execute(query)

        return list(result.scalars().all())

    async def add(self, application: VolunteerApplication):
        self._session.add(application)
        await self._session.commit()
        await self._session.refresh(application)

        query = (
            select(VolunteerApplication)
            .where(VolunteerApplication.id == application.id)
            .options(
                selectinload(VolunteerApplication.event).selectinload(Event.status),
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    async def count_by_event(self, event_id: int) -> int:
        query = select(func.count()).select_from(VolunteerApplication).where(
            VolunteerApplication.event_id == event_id
        )
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_by_user_and_event(self, user_id: int, event_id: int):
        query = select(VolunteerApplication).where(
            VolunteerApplication.user_id == user_id,
            VolunteerApplication.event_id == event_id,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, application: VolunteerApplication) -> None:
        await self._session.delete(application)
        await self._session.commit()

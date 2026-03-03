from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.event import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    model = Event

    async def events(self, offset: int, limit: int) -> list:
        query = (
            select(Event)
            .options(selectinload(Event.status))
            .offset(offset)
            .limit(limit)
            .order_by(Event.id.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def detail(self, event_id: int):
        query = select(Event).where(Event.id == event_id).options(selectinload(Event.status))
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def add(self, event: Event) -> Event:
        self._session.add(event)
        await self._session.commit()
        await self._session.refresh(event)
        query = select(Event).where(Event.id == event.id).options(selectinload(Event.status))
        result = await self._session.execute(query)
        return result.scalar_one()

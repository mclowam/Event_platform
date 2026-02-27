from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.session import SessionDep
from fastapi import Request, HTTPException, Query

from models import Event


class EventRepository:
    def __init__(self, session: SessionDep) -> None:
        self._session = session

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

        return event

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.permissions import is_organizer
from db.session import SessionDep
from models.event import Event
from schemas.event import EventResponseSchema, EventSchema
from schemas.user import UserPayload
from models.status import Status
event_router = APIRouter(
    prefix="/events",
)


@event_router.get("", response_model=list[EventResponseSchema])
async def all_events(session: SessionDep):
    query = select(Event).options(selectinload(Event.status))
    result = await session.execute(query)
    return result.scalars().all()

@event_router.post("", response_model=EventResponseSchema)
async def create_event(
        data: EventSchema,
        session: SessionDep,
        user: UserPayload = Depends(is_organizer)
):
    new_event = Event(
        title=data.title,
        description=data.description,
        location=data.location,
        organizer_id=user.user_id,
        status_id=data.status_id,
        start_time=data.start_time,
        end_time=data.end_time,
    )

    session.add(new_event)
    await session.commit()

    query = (
        select(Event)
        .where(Event.id == new_event.id)
        .options(selectinload(Event.status))
    )
    result = await session.execute(query)
    return result.scalar_one()
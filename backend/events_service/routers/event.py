from fastapi import APIRouter, HTTPException, status, Response
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.permissions import is_organizer, is_admin, is_organizer_or_admin
from db.session import SessionDep
from models.event import Event
from schemas.event import EventResponseSchema, EventSchema, EventUpdateSchema
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
        user: UserPayload = Depends(is_organizer_or_admin)
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


@event_router.get("/{event_id}", response_model=EventResponseSchema)
async def get_event(event_id: int, session: SessionDep):
    query = (
        select(Event)
        .where(Event.id == event_id)
        .options(selectinload(Event.status))
    )
    result = await session.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@event_router.patch("/{event_id}", response_model=EventResponseSchema)
async def update_event(
        event_id: int,
        data: EventUpdateSchema,
        session: SessionDep,
        user: UserPayload = Depends(is_organizer_or_admin)
):
    query = select(Event).where(Event.id == event_id).options(selectinload(Event.status))
    result = await session.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(404, "Event not found")

    if event.organizer_id != user.user_id and user.role != 'admin':
        raise HTTPException(403, "You don't have permission to edit this event")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    await session.commit()
    await session.refresh(event)
    return event


@event_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
        event_id: int,
        session: SessionDep,
        user: UserPayload = Depends(is_organizer_or_admin)
):
    query = select(Event).where(Event.id == event_id)
    result = await session.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(404, "Event not found")

    if event.organizer_id != user.user_id and user.role != 'admin':
        raise HTTPException(403, "You don't have permission to delete this event")

    await session.delete(event)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

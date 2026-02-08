from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.auth import get_current_user
from db.session import SessionDep
from models.attendee import Attendee
from models.event import Event
from schemas.attendee import AttendeeResponseSchema, AttendeeSchema
from schemas.user import UserPayload

attendee_router = APIRouter(
    prefix="/attendee/events"
)


@attendee_router.get("", response_model=list[AttendeeResponseSchema])
async def all_attendees(session: SessionDep, user: UserPayload = Depends(get_current_user)):
    query = (
        select(Attendee)
        .where(Attendee.user_id == user.user_id)
        .options(
            selectinload(Attendee.events)
            .selectinload(Event.status)
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


@attendee_router.post("", response_model=AttendeeResponseSchema)
async def create_attendee(
        session: SessionDep,
        data: AttendeeSchema,
        user: UserPayload = Depends(get_current_user)
):
    new_attendee = Attendee(
        user_id=user.user_id,
        event_id=data.event_id,
    )
    session.add(new_attendee)
    await session.commit()

    query = (
        select(Attendee)
        .where(Attendee.id == new_attendee.id)
        .options(
            selectinload(Attendee.events)
            .selectinload(Event.status)
        )
    )
    result = await session.execute(query)
    return result.scalar_one()


@attendee_router.get("/{event_id}", response_model=AttendeeResponseSchema)
async def get_registration_status(
        event_id: int,
        session: SessionDep,
        user: UserPayload = Depends(get_current_user)
):
    query = (
        select(Attendee)
        .where(Attendee.user_id == user.user_id, Attendee.event_id == event_id)
        .options(selectinload(Attendee.events).selectinload(Event.status))
    )
    result = await session.execute(query)
    reg = result.scalar_one_or_none()
    if not reg:
        raise HTTPException(404, "You are not registered to this event")
    return reg


@attendee_router.delete("/{event_id}", status_code=204)
async def leave_event(
        event_id: int,
        session: SessionDep,
        user: UserPayload = Depends(get_current_user)
):
    query = select(Attendee).where(
        Attendee.user_id == user.user_id,
        Attendee.event_id == event_id
    )
    result = await session.execute(query)
    reg = result.scalar_one_or_none()

    if not reg:
        raise HTTPException(404, "Запись не найдена")

    await session.delete(reg)
    await session.commit()
    return Response(status_code=204)

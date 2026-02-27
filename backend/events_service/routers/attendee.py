from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from db.session import SessionDep
from models import VolunteerApplication, Event
from core.auth import get_current_user
from schemas.attendee import ApplicationResponseSchema, ApplicationCreateSchema
from schemas.user import UserPayload

application_router = APIRouter(prefix="/applications", redirect_slashes=False)


@application_router.get("", response_model=list[ApplicationResponseSchema])
async def my_applications(
    session: SessionDep,
    user: UserPayload = Depends(get_current_user)
):
    query = (
        select(VolunteerApplication)
        .where(VolunteerApplication.user_id == user.user_id)
        .options(
            selectinload(VolunteerApplication.event)
            .selectinload(Event.status)
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


@application_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_application(
        event_id: int,
        session: SessionDep,
        user: UserPayload = Depends(get_current_user)
):
    query = select(VolunteerApplication).where(
        VolunteerApplication.user_id == user.user_id,
        VolunteerApplication.event_id == event_id
    )
    result = await session.execute(query)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    await session.delete(app)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@application_router.post("", response_model=ApplicationResponseSchema)
async def apply_for_event(
        session: SessionDep,
        data: ApplicationCreateSchema,
        user: UserPayload = Depends(get_current_user)
):
    event_id = data.event_id

    event = await session.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")

    count_query = select(func.count()).select_from(VolunteerApplication).where(
        VolunteerApplication.event_id == event_id
    )
    current_count = (await session.execute(count_query)).scalar()

    if event.max_volunteers > 0 and current_count >= event.max_volunteers:
        raise HTTPException(400, "All volunteer spots for this event are already taken")

    new_app = VolunteerApplication(user_id=user.user_id, event_id=event_id)
    try:
        session.add(new_app)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(400, "You have already applied for this event")

    query = (
        select(VolunteerApplication)
        .where(VolunteerApplication.id == new_app.id)
        .options(
            selectinload(VolunteerApplication.event)
            .selectinload(Event.status)
        )
    )
    result = await session.execute(query)
    full_app = result.scalar_one()

    return full_app
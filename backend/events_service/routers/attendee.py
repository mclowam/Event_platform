from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from db.session import SessionDep
from models import VolunteerApplication, Event
from core.auth import get_current_user
from schemas.attendee import ApplicationResponseSchema, ApplicationCreateSchema
from schemas.user import UserPayload
from services import ApplicationRepository, EventRepository
from services.application_service import ApplicationService

application_router = APIRouter(prefix="/applications", redirect_slashes=False)

def get_application_service(session: SessionDep) -> ApplicationService:
        return ApplicationService(
            application_repository=ApplicationRepository(session),
            event_repository=EventRepository(session)
        )


@application_router.get("", response_model=list[ApplicationResponseSchema])
async def my_applications(
    session: SessionDep,
    user: UserPayload = Depends(get_current_user)
):
    service = get_application_service(session)
    return await service.my_applications(user)


@application_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_application(
        event_id: int,
        session: SessionDep,
        user: UserPayload = Depends(get_current_user)
):
    service = get_application_service(session)
    return await service.cancel_application(event_id=event_id, user=user)


@application_router.post("", response_model=ApplicationResponseSchema)
async def apply_for_event(
        session: SessionDep,
        data: ApplicationCreateSchema,
        user: UserPayload = Depends(get_current_user)
):
    service = get_application_service(session)
    return await service.apply_for_event(data=data, user=user)
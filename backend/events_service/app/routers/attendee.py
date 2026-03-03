from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_session
from app.schemas.attendee import ApplicationResponseSchema, ApplicationCreateSchema
from app.schemas.user import UserPayload
from app.repositories.application_repository import ApplicationRepository
from app.repositories.event_repository import EventRepository
from app.services.application_service import ApplicationService

application_router = APIRouter(prefix="/applications", redirect_slashes=False)


def get_application_service(session: AsyncSession = Depends(get_session)) -> ApplicationService:
    return ApplicationService(
        application_repository=ApplicationRepository(session),
        event_repository=EventRepository(session),
    )


@application_router.get("", response_model=list[ApplicationResponseSchema])
async def my_applications(
    user: UserPayload = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    return await service.my_applications(user)


@application_router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_application(
    event_id: int,
    user: UserPayload = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    await service.cancel_application(user=user, event_id=event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@application_router.post("", response_model=ApplicationResponseSchema)
async def apply_for_event(
    data: ApplicationCreateSchema,
    user: UserPayload = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    return await service.apply_for_event(data=data, user=user)

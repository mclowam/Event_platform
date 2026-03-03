from datetime import datetime

from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import is_organizer_or_admin
from app.db.session import get_session
from app.schemas.event import EventResponseSchema
from app.schemas.user import UserPayload
from app.repositories.event_repository import EventRepository
from app.services.image_storage import MinioImageStorage
from app.services.event_service import EventService

event_router = APIRouter(prefix="/events", redirect_slashes=False)


def get_event_service(session: AsyncSession = Depends(get_session)) -> EventService:
    return EventService(
        event_repository=EventRepository(session),
        image_storage=MinioImageStorage(),
    )


@event_router.get("", response_model=list[EventResponseSchema])
async def all_events(
    request: Request,
    service: EventService = Depends(get_event_service),
    page: int = Query(1, ge=1),
    size: int = Query(2, ge=1, le=100),
):
    return await service.list_events(request=request, page=page, size=size)


@event_router.get("/{event_id}", response_model=EventResponseSchema)
async def get_one_event(
    event_id: int,
    request: Request,
    service: EventService = Depends(get_event_service),
):
    return await service.event_detail(request=request, event_id=event_id)


@event_router.get("/{event_id}/image")
async def get_event_image(
    event_id: int,
    service: EventService = Depends(get_event_service),
):
    return await service.get_event_image(event_id=event_id)


@event_router.post("", response_model=EventResponseSchema)
async def create_event(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    status_id: int = Form(...),
    max_volunteers: int = Form(0),
    start_time: datetime = Form(...),
    end_time: datetime = Form(...),
    file: UploadFile = File(...),
    user: UserPayload = Depends(is_organizer_or_admin),
    service: EventService = Depends(get_event_service),
):
    return await service.create_event(
        request=request,
        user=user,
        title=title,
        description=description,
        location=location,
        status_id=status_id,
        max_volunteers=max_volunteers,
        start_time=start_time,
        end_time=end_time,
        file=file,
    )

import io
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, UploadFile, File, Request, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.permissions import is_organizer_or_admin
from db.session import SessionDep
from schemas.event import EventResponseSchema
from schemas.user import UserPayload

from core.minio_client import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    session_minio,
    MINIO_BUCKET
)
from models import Event, Status
from services import EventRepository, MinioImageStorage
from services.event_service import EventService

event_router = APIRouter(
    prefix="/events",
    redirect_slashes=False
)


def get_event_service(session: SessionDep) -> EventService:
    return EventService(
        event_repository=EventRepository(session),
        image_storage=MinioImageStorage()
    )


@event_router.get("", response_model=list[EventResponseSchema])
async def all_events(
        request: Request,
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(2, ge=1, le=100)
):
    service = get_event_service(session)
    return await service.list_events(request=request, page=page, size=size)


@event_router.get("/{event_id}", response_model=EventResponseSchema)
async def get_one_event(event_id: int, request: Request, session: SessionDep):
    service = get_event_service(session)
    return await service.event_detail(request=request, event_id=event_id)


@event_router.get("/{event_id}/image")
async def get_event_image(session: SessionDep, event_id: int):
    service = get_event_service(session)
    return await service.get_event_image(event_id=event_id)


@event_router.post("", response_model=EventResponseSchema)
async def create_event(
        request: Request,
        session: SessionDep,
        title: str = Form(...),
        description: str = Form(...),
        location: str = Form(...),
        status_id: int = Form(...),
        max_volunteers: int = Form(0),
        start_time: datetime = Form(...),
        end_time: datetime = Form(...),
        file: UploadFile = File(...),
        user: UserPayload = Depends(is_organizer_or_admin)
):
    service = get_event_service(session)
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
        file=file
    )

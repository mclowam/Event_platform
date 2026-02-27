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

event_router = APIRouter(
    prefix="/events",
    redirect_slashes=False
)


def get_image_proxy_url(request: Request, event_id: int) -> str:
    base = str(request.base_url).rstrip('/')
    return f"{base}/events/{event_id}/image"


@event_router.get("", response_model=list[EventResponseSchema])
async def all_events(
        request: Request,
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(2, ge=1, le=100)
):
    ...

@event_router.get("/{event_id}", response_model=EventResponseSchema)
async def get_one_event(event_id: int, request: Request, session: SessionDep):
    query = select(Event).where(Event.id == event_id).options(selectinload(Event.status))
    result = await session.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    if event.image_url:
        event.image_url = get_image_proxy_url(request, event.id)
    return event


@event_router.get("/{event_id}/image")
async def get_event_image(event_id: int, session: SessionDep):
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event or not event.image_url:
        raise HTTPException(status_code=404, detail="Изображение не найдено")

    async with session_minio.client("s3", endpoint_url=MINIO_ENDPOINT,
                                    aws_access_key_id=MINIO_ACCESS_KEY,
                                    aws_secret_access_key=MINIO_SECRET_KEY) as s3:
        try:
            response = await s3.get_object(Bucket=MINIO_BUCKET, Key=event.image_url)
            data = await response['Body'].read()
            return StreamingResponse(
                io.BytesIO(data),
                media_type=response.get('ContentType', 'image/jpeg')
            )
        except Exception:
            raise HTTPException(status_code=404, detail="Ошибка при чтении файла из хранилища")


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
    filename = None
    if file:
        filename = f"{uuid.uuid4()}_{file.filename}"
        async with session_minio.client("s3", endpoint_url=MINIO_ENDPOINT,
                                        aws_access_key_id=MINIO_ACCESS_KEY,
                                        aws_secret_access_key=MINIO_SECRET_KEY) as s3:
            await s3.upload_fileobj(file.file, MINIO_BUCKET, filename)

    new_event = Event(
        title=title,
        description=description,
        location=location,
        organizer_id=user.user_id,
        max_volunteers=max_volunteers,
        status_id=status_id,
        start_time=start_time,
        end_time=end_time,
        image_url=filename
    )

    session.add(new_event)
    await session.commit()

    await session.refresh(new_event)

    query = (
        select(Event)
        .where(Event.id == new_event.id)
        .options(selectinload(Event.status))
    )
    result = await session.execute(query)
    event_obj = result.scalar_one()

    if event_obj.image_url:
        event_obj.image_url = get_image_proxy_url(request, event_obj.id)

    return event_obj
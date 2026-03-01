import io
import uuid
from datetime import datetime

from starlette.responses import StreamingResponse

from core.minio_client import session_minio, MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
from models import Event
from schemas.user import UserPayload
from services import EventRepository, IEventRepository, MinioImageStorage
from fastapi import Request, UploadFile, HTTPException


class EventService:
    def __init__(
            self,
            event_repository: IEventRepository,
            image_storage: MinioImageStorage,
    ):
        self._events = event_repository
        self._images = image_storage

    @staticmethod
    def image_proxy_url(request: Request, event_id: int) -> str:
        base = str(request.base_url).rstrip("/")
        return f"{base}/events/{event_id}/image"

    async def list_events(
            self,
            request: Request,
            page: int,
            size: int
    ):
        offset = (page - 1) * size
        events = await self._events.events(offset=offset, limit=size)

        for event in events:
            if event.image_url:
                event.image_url = self.image_proxy_url(request, event.id)
        return events

    async def event_detail(self, request: Request, event_id: int):
        event = await self._events.detail(event_id)

        if event.image_url:
            event.image_url = self.image_proxy_url(request, event.id)

        return event

    async def get_event_image(self, event_id: int) -> StreamingResponse:
        event = await self._events.detail(event_id)
        if not event or not event.image_url:
            raise HTTPException(status_code=404, detail="Изображение не найдено")
        try:
            data, content_type = await self._images.get_bytes(event.image_url)
            return StreamingResponse(io.BytesIO(data), media_type=content_type)
        except Exception:
            raise HTTPException(status_code=404, detail="Ошибка при чтении файла из хранилища")

    async def create_event(
            self,
            request: Request,
            user: UserPayload,
            title: str,
            description: str,
            location: str,
            status_id: int,
            max_volunteers: int,
            start_time: datetime,
            end_time: datetime,
            file: UploadFile,
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
        event = await self._events.add(new_event)
        if event.image_url:
            event.image_url = self.image_proxy_url(request, event.id)
        return event

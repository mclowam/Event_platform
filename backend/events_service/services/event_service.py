from services import EventRepository, IEventRepository, MinioImageStorage
from fastapi import Request

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


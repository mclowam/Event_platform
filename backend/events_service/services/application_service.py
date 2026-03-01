from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from models import VolunteerApplication, Event
from schemas.attendee import ApplicationCreateSchema
from schemas.user import UserPayload
from services import IApplicationRepository, IEventRepository


class ApplicationService:
    def __init__(
            self,
            application_repository: IApplicationRepository,
            event_repository: IEventRepository,
    ):
        self._applications = application_repository
        self._events = event_repository

    async def my_applications(self, user: UserPayload):
        return await self._applications.my_applications(user.user_id)

    async def apply_for_event(self,
                              data: ApplicationCreateSchema,
                              user: UserPayload
                              ):
        event_id = data.event_id
        event = await self._events.detail(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        current_count = await self._applications.count_by_event(event_id)

        if event.max_volunteers > 0 and current_count >= event.max_volunteers:
            raise HTTPException(
                400,
                "All volunteer spots for this event are already taken",
            )
        new_app = VolunteerApplication(user_id=user.user_id, event_id=event_id)

        try:
            return await self._applications.add(new_app)
        except IntegrityError:
            raise HTTPException(400, "You have already applied for this event")

    async def cancel_application(self, user: UserPayload, event_id: int) -> None:
        app = await self._applications.get_by_user_and_event(user.user_id, event_id)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        await self._applications.delete(app)

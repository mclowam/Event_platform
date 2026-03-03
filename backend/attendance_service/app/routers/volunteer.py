from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_session
from app.models.attendance import Attendance
from app.schemas.user import UserPayload
from app.utils import tokens
from app.services import qr_service

volunteer_router = APIRouter(prefix="/volunteers")


@volunteer_router.get("/qr/{event_id}")
async def get_my_qr(event_id: int, user: UserPayload = Depends(get_current_user)):
    token_str = tokens.create_attendance_token(user.user_id, event_id)
    qr_image = await qr_service.generate_qr_code(token_str)
    return StreamingResponse(qr_image, media_type="image/png")


@volunteer_router.get("/hours")
async def all_volunteer_hours(
    session: AsyncSession = Depends(get_session),
    user: UserPayload = Depends(get_current_user),
):
    query = select(Attendance).where(Attendance.user_id == user.user_id)
    result = (await session.execute(query)).scalars().all()
    total_hours = sum(row.hours_worked for row in result)
    return {"total_hours": total_hours}

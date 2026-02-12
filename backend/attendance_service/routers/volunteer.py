from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from core.auth import get_current_user
from schemas.user import UserPayload
from utils import tokens
from services import qr_service

volunteer_router = APIRouter(prefix="/volunteers")


@volunteer_router.get("/qr/{event_id}")
async def get_my_qr(event_id: int, user: UserPayload = Depends(get_current_user)):

    user_id = user.user_id
    token_str = tokens.create_attendance_token(user_id, event_id)

    qr_image = await qr_service.generate_qr_code(token_str)

    return StreamingResponse(qr_image, media_type="image/png")
from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from core.auth import get_current_user
from db.session import SessionDep
from schemas.organizer import ScanResponse, ScanRequest
from schemas.user import UserPayload
from services.attendance import process_scan

organizer_router = APIRouter(
    prefix="/organizers",
)


@organizer_router.post("/scan", response_model=ScanResponse)
async def scan_qr(
        body: ScanRequest,
        session: SessionDep,
        user: UserPayload = Depends(get_current_user)
):

    result = await process_scan(
        session=session,
        scanner_id=user.user_id,
        qr_token=body.qr_token
    )

    att_obj = result["obj"]

    return ScanResponse(
        status=result["status"],
        message=result["message"],

        volunteer_id=att_obj.user_id,
        event_id=att_obj.event_id,
        current_state=att_obj.status,
        check_in_at=att_obj.check_in_at,
        check_out_at=att_obj.check_out_at,
        hours_worked=att_obj.hours_worked
    )


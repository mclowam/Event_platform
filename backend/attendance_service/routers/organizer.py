from fastapi import Depends, HTTPException, APIRouter
from starlette import status

from core.auth import get_current_user
from core.permissions import is_organizer_or_admin
from db.session import SessionDep
from schemas.attendance import ManualAttendanceRequest
from schemas.organizer import ScanResponse, ScanRequest
from schemas.user import UserPayload
from services.attendance import process_scan, process_email_checkin
from services.stats import stats_event

organizer_router = APIRouter(
    prefix="/organizers",
)


@organizer_router.post("/attendance/qr", response_model=ScanResponse)
async def scan_qr(
        body: ScanRequest,
        session: SessionDep,
        user: UserPayload = Depends(is_organizer_or_admin)
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


@organizer_router.post("/attendance/email", response_model=ScanResponse)
async def manual_checkin(
        body: ManualAttendanceRequest,
        session: SessionDep,
        user: UserPayload = Depends(is_organizer_or_admin)
):
    result = await process_email_checkin(
        session=session,
        scanner_id=user.user_id,
        email=body.email,
        event_id=body.event_id
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


@organizer_router.get("/attendance/stats")
async def get_stats(
        session: SessionDep,
        event_id: int,
        user: UserPayload = Depends(is_organizer_or_admin)
):
    stats = await stats_event(session=session, event_id=event_id)

    return stats
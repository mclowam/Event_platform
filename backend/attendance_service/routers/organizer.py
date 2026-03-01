from fastapi import APIRouter, Depends
from db.session import SessionDep
from core.auth import get_current_user
from core.permissions import is_organizer_or_admin
from schemas.attendance import ManualAttendanceRequest
from schemas.organizer import ScanResponse, ScanRequest
from schemas.user import UserPayload
from services.scan_service import AttendanceScanService
from services.stats_service import AttendanceStatsService
from services.attendance_repository import AttendanceRepository
from services.token_decoder import AttendanceTokenDecoder
from services.user_resolver import AuthServiceUserResolver

organizer_router = APIRouter(prefix="/organizers")


def get_scan_service(session: SessionDep) -> AttendanceScanService:
    return AttendanceScanService(
        attendance_repository=AttendanceRepository(session),
        token_decoder=AttendanceTokenDecoder(),
        user_resolver=AuthServiceUserResolver(),
    )


def get_stats_service(session: SessionDep) -> AttendanceStatsService:
    return AttendanceStatsService(stats_repository=AttendanceRepository(session))


def _to_scan_response(result: dict) -> ScanResponse:
    att = result["obj"]
    return ScanResponse(
        status=result["status"],
        message=result["message"],
        volunteer_id=att.user_id,
        event_id=att.event_id,
        current_state=att.status,
        check_in_at=att.check_in_at,
        check_out_at=att.check_out_at,
        hours_worked=att.hours_worked,
    )


@organizer_router.post("/attendance/qr", response_model=ScanResponse)
async def scan_qr(
    body: ScanRequest,
    session: SessionDep,
    user: UserPayload = Depends(is_organizer_or_admin),
):
    service = get_scan_service(session)
    result = await service.process_scan(
        scanner_id=user.user_id,
        qr_token=body.qr_token,
    )
    return _to_scan_response(result)


@organizer_router.post("/attendance/email", response_model=ScanResponse)
async def manual_checkin(
    body: ManualAttendanceRequest,
    session: SessionDep,
    user: UserPayload = Depends(is_organizer_or_admin),
):
    service = get_scan_service(session)
    result = await service.process_email_checkin(
        scanner_id=user.user_id,
        email=body.email,
        event_id=body.event_id,
    )
    return _to_scan_response(result)


@organizer_router.get("/attendance/stats")
async def get_stats(
    session: SessionDep,
    event_id: int,
    user: UserPayload = Depends(is_organizer_or_admin),
):
    service = get_stats_service(session)
    return await service.get_stats(event_id=event_id)
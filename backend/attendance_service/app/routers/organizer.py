from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import is_organizer_or_admin
from app.db.session import get_session
from app.schemas.attendance import ManualAttendanceRequest
from app.schemas.organizer import ScanResponse, ScanRequest
from app.schemas.user import UserPayload
from app.repositories.attendance_repository import AttendanceRepository
from app.services.scan_service import AttendanceScanService
from app.services.stats_service import AttendanceStatsService
from app.services.token_decoder import AttendanceTokenDecoder
from app.services.user_resolver import AuthServiceUserResolver

organizer_router = APIRouter(prefix="/organizers")


def get_scan_service(session: AsyncSession = Depends(get_session)) -> AttendanceScanService:
    return AttendanceScanService(
        attendance_repository=AttendanceRepository(session),
        token_decoder=AttendanceTokenDecoder(),
        user_resolver=AuthServiceUserResolver(),
    )


def get_stats_service(session: AsyncSession = Depends(get_session)) -> AttendanceStatsService:
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
    user: UserPayload = Depends(is_organizer_or_admin),
    service: AttendanceScanService = Depends(get_scan_service),
):
    result = await service.process_scan(scanner_id=user.user_id, qr_token=body.qr_token)
    return _to_scan_response(result)


@organizer_router.post("/attendance/email", response_model=ScanResponse)
async def manual_checkin(
    body: ManualAttendanceRequest,
    user: UserPayload = Depends(is_organizer_or_admin),
    service: AttendanceScanService = Depends(get_scan_service),
):
    result = await service.process_email_checkin(
        scanner_id=user.user_id, email=body.email, event_id=body.event_id,
    )
    return _to_scan_response(result)


@organizer_router.get("/attendance/stats")
async def get_stats(
    event_id: int,
    user: UserPayload = Depends(is_organizer_or_admin),
    service: AttendanceStatsService = Depends(get_stats_service),
):
    return await service.get_stats(event_id=event_id)

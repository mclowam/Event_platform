
from datetime import datetime, timezone

from fastapi import HTTPException

from models.attendance import Attendance, AttendanceStatus

from .abstractions import IAttendanceRepository, ITokenDecoder, IUserResolver


class AttendanceScanService:

    MIN_CHECKOUT_SECONDS = 60

    def __init__(
        self,
        attendance_repository: IAttendanceRepository,
        token_decoder: ITokenDecoder,
        user_resolver: IUserResolver,
    ) -> None:
        self._repo = attendance_repository
        self._decoder = token_decoder
        self._user_resolver = user_resolver

    async def process_scan(self, scanner_id: int, qr_token: str) -> dict:
        payload = self._decoder.decode(qr_token)
        if not payload:
            raise HTTPException(status_code=400, detail="Invalid or expired QR code")
        user_id = int(payload.get("sub") or payload.get("user_id"))
        event_id = int(payload["event_id"])
        attendance = await self._repo.get_by_event_and_user(event_id, user_id)
        return await self._apply_scan_result(scanner_id, attendance, user_id, event_id)

    async def process_email_checkin(
        self,
        scanner_id: int,
        email: str,
        event_id: int,
    ) -> dict:
        user = await self._user_resolver.get_user_by_email(email)
        if not user:
            raise HTTPException(404, "User with this email does not exist")
        attendance = await self._repo.get_by_event_and_user(event_id, user.user_id)
        return await self._apply_scan_result(
            scanner_id, attendance, user.user_id, event_id
        )

    async def _apply_scan_result(
        self,
        scanner_id: int,
        attendance: Attendance | None,
        user_id: int,
        event_id: int,
    ) -> dict:
        utc_now = datetime.now(timezone.utc)

        if not attendance:
            new_attendance = Attendance(
                event_id=event_id,
                user_id=user_id,
                verified_by=scanner_id,
                status=AttendanceStatus.CHECKED_IN,
                hours_worked=0.0,
                check_in_at=utc_now,
            )
            await self._repo.add(new_attendance)
            return {
                "status": "success",
                "message": "Check-in successful",
                "obj": new_attendance,
            }

        if attendance.status == AttendanceStatus.CHECKED_IN:
            elapsed = (utc_now - attendance.check_in_at).total_seconds()
            if elapsed < self.MIN_CHECKOUT_SECONDS:
                return {
                    "status": "warning",
                    "message": "Too early to check out. Please wait a minute.",
                    "obj": attendance,
                }
            attendance.status = AttendanceStatus.COMPLETED
            attendance.check_out_at = utc_now
            attendance.verified_by = scanner_id
            attendance.hours_worked = round(elapsed / 3600, 2)
            await self._repo.update(attendance)
            return {
                "status": "success",
                "message": f"Shift completed. Hours worked: {attendance.hours_worked}",
                "obj": attendance,
            }

        if attendance.status == AttendanceStatus.COMPLETED:
            return {
                "status": "warning",
                "message": "Shift was already closed.",
                "obj": attendance,
            }

        return {
            "status": "error",
            "message": "Unknown status",
            "obj": attendance,
        }

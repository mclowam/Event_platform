from datetime import datetime, timezone
from sqlalchemy import select
from fastapi import HTTPException

from db.session import SessionDep
from models.attendance import Attendance, AttendanceStatus
from utils.tokens import decode_attendance_token
from utils.users import get_user_by_email


async def process_scan(
        session: SessionDep,
        scanner_id: int,
        qr_token: str
):
    payload = decode_attendance_token(qr_token)

    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired QR code")

    user_id = int(payload.get('sub') or payload.get('user_id'))
    event_id = int(payload['event_id'])

    query = select(Attendance).where(
        Attendance.event_id == event_id,
        Attendance.user_id == user_id
    )
    attendance = (await session.execute(query)).scalar_one_or_none()

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
        session.add(new_attendance)
        await session.commit()
        await session.refresh(new_attendance)

        return {
            "status": "success",
            "message": "Check-in successful",
            "obj": new_attendance
        }

    elif attendance.status == AttendanceStatus.CHECKED_IN:
        if (utc_now - attendance.check_in_at).total_seconds() < 60:
            return {
                "status": "warning",
                "message": "Too early to check out. Please wait a minute.",
                "obj": attendance
            }

        delta_seconds = (utc_now - attendance.check_in_at).total_seconds()

        attendance.status = AttendanceStatus.COMPLETED
        attendance.check_out_at = utc_now
        attendance.verified_by = scanner_id
        attendance.hours_worked = round(delta_seconds / 3600, 2)

        await session.commit()
        await session.refresh(attendance)

        return {
            "status": "success",
            "message": f"Shift completed. Hours worked: {attendance.hours_worked}",
            "obj": attendance
        }

    elif attendance.status == AttendanceStatus.COMPLETED:
        return {
            "status": "warning",
            "message": "Shift was already closed.",
            "obj": attendance
        }

    return {
        "status": "error",
        "message": "Unknown status",
        "obj": attendance
    }


async def _handle_attendance_logic(session: SessionDep, attendance: Attendance, user_id: int, event_id: int, scanner_id: int):
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
        session.add(new_attendance)
        await session.commit()
        await session.refresh(new_attendance)
        return {"status": "success", "message": "Вход выполнен (Ручной) ✅", "obj": new_attendance}

    elif attendance.status == AttendanceStatus.CHECKED_IN:
        if (utc_now - attendance.check_in_at).total_seconds() < 60:
             return {"status": "warning", "message": "Рано выходить", "obj": attendance}

        delta_seconds = (utc_now - attendance.check_in_at).total_seconds()
        attendance.status = AttendanceStatus.COMPLETED
        attendance.check_out_at = utc_now
        attendance.verified_by = scanner_id
        attendance.hours_worked = round(delta_seconds / 3600, 2)

        await session.commit()
        await session.refresh(attendance)
        return {"status": "success", "message": f"Смена закрыта. {attendance.hours_worked} ч.", "obj": attendance}

    return {"status": "warning", "message": "Уже закрыто", "obj": attendance}


async def process_email_checkin(session: SessionDep, scanner_id: int, email: str, event_id: int):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Пользователь с таким email не найден")

    query = select(Attendance).where(
        Attendance.user_id == user.user_id,
        Attendance.event_id == event_id
    )
    attendance = (await session.execute(query)).scalar_one_or_none()

    return await _handle_attendance_logic(session, attendance, user.user_id, event_id, scanner_id)
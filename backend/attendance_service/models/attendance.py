from datetime import datetime
from sqlalchemy import Integer, DateTime, func, String, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base
from schemas.attendance import AttendanceStatus


class Attendance(Base):
    __tablename__ = 'attendance'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus),
        default=AttendanceStatus.REGISTERED,
        nullable=False
    )

    check_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    check_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    hours_worked: Mapped[float] = mapped_column(Float, default=0.0)

    verified_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
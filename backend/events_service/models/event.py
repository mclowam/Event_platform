from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    organizer_id: Mapped[int] = mapped_column(Integer)
    location: Mapped[str] = mapped_column(String)
    max_volunteers: Mapped[int] = mapped_column(Integer, default=0)
    status_id: Mapped[int] = mapped_column(ForeignKey('statuses.id'))
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    status: Mapped["Status"] = relationship("Status", back_populates="events")

    applications: Mapped[list["VolunteerApplication"]] = relationship(
        "VolunteerApplication",
        back_populates="event",
        cascade="all, delete-orphan"
    )
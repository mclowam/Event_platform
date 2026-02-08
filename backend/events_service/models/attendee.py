from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Attendee(Base):
    __tablename__ = 'event_attendees'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='_event_user_uc'),
    )

    events: Mapped["Event"] = relationship(
        "Event",
        back_populates="attendee",
    )
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Status(Base):
    __tablename__ = 'statuses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="status")


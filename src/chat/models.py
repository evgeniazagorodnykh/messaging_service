from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database import Base


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)

    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages"
    )

    def mark_as_read(self):
        """Отметить сообщение как прочитанное"""
        self.read = True
        self.read_at = datetime.utcnow()

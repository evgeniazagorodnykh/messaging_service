from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import (TIMESTAMP, Boolean, Column, Integer, String)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.password import PasswordHelper

from database import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    telegram_id: Mapped[str] = mapped_column(
        String(length=320), unique=True, nullable=True
    )
    registered_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    password_helper = PasswordHelper()

    sent_messages: Mapped[List["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.receiver_id]",
        back_populates="receiver"
    )

    def verify_password(self, password: str) -> bool:
        """Проверка пароля пользователя."""
        return self.password_helper.verify_and_update(password, self.hashed_password)

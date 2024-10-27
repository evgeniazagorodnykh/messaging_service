from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    receiver_id: int


class MessageRead(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    sent_at: datetime
    read: bool
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

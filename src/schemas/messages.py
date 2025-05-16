from datetime import datetime

from pydantic import BaseModel


class MessageAdd(BaseModel):
    sender_id: int
    recipient_id: int
    content: str


class Message(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    created_at: datetime

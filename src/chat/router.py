import asyncio
from typing import List

from fastapi import APIRouter, Body, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from chat.models import Message
from chat.schemas import MessageRead
from database import async_session_maker, get_async_session
from auth.base_config import fastapi_users

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except RuntimeError:
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


async def get_current_user_optional(
    current_user: User = Depends(fastapi_users.current_user(optional=True))
):
    return current_user


@router.post("/messages/send")
async def send_message(
    receiver_id: int = Body(...), 
    content: str = Body(...),
    session: AsyncSession = Depends(get_async_session),
    sender: User = Depends(get_current_user_optional)
):
    async with session:
        result = await session.execute(select(User).where(User.id == receiver_id))
        receiver = result.scalars().first()

        if not sender or not receiver:
            raise HTTPException(status_code=400, detail="Sender or receiver not found")
        
        message = Message(
            content=content,
            sender_id=sender.id,
            receiver_id=receiver_id,
            delivered=False
        )
        session.add(message)
        await session.flush()
        # await session.commit()
        # await session.refresh(message)

        if receiver_id in manager.active_connections:
            await manager.send_personal_message(f"{sender.username}: {content}", receiver_id)
            message.delivered = True
        
        await session.commit()

    return {"status": "Message sent"}


@router.get("/messages/{chat_user_id}", response_model=List[MessageRead])
async def get_user_messages(
    chat_user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        raise HTTPException(status_code=400, detail="Not authenticated")
    result = await session.execute(
        select(Message)
        .where(
            (Message.sender_id == current_user.id) & (Message.receiver_id == chat_user_id) |
            (Message.sender_id == chat_user_id) & (Message.receiver_id == current_user.id)
        )
        .order_by(Message.sent_at)
    )
    messages = result.scalars().all()
    return messages


@router.post("/messages/{message_id}/read")
async def mark_message_as_read(
    message_id: int, session: AsyncSession = Depends(get_async_session)
):
    message = await session.get(Message, message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.mark_as_read()
    await session.commit()

    return {"status": "Message marked as read"}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    # session: AsyncSession = Depends(get_async_session)
):
    await manager.connect(websocket, user_id)

    # Открываем отдельную сессию внутри WebSocket-коннекшена
    async with async_session_maker() as session:
        # Проверка и отправка недоставленных сообщений
        result = await session.execute(
            select(Message).where(Message.receiver_id == user_id, Message.delivered == False)
        )
        undelivered_messages = result.scalars().all()

        for message in undelivered_messages:
            await manager.send_personal_message(f"{message.sender.username}: {message.content}", user_id)
            # Обновление статуса сообщения как доставленное
            message.delivered = True

        await session.commit()

    # # Проверяем, есть ли недоставленные сообщения
    # result = await session.execute(
    #     select(Message).where(Message.receiver_id == user_id, Message.delivered == False)
    # )
    # undelivered_messages = result.scalars().all()

    # for message in undelivered_messages:
    #     # Отправляем недоставленные сообщения
    #     await manager.send_personal_message(f"{message.sender.username}: {message.content}", user_id)
    #     # Обновляем статус сообщения как доставленное
    #     message.delivered = True
    #     await session.commit()

    try:
        while True:
            data = await websocket.receive_text()
            async with async_session_maker() as session:
                message = await session.execute(
                    select(Message).where(Message.receiver_id == user_id)
                )
                message = message.scalars().first()
            
                if message:
                    await manager.send_personal_message(f"{message.sender.username}: {message.content}", user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)

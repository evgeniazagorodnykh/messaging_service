import httpx
import asyncio

from celery import Celery
from sqlalchemy.future import select

from database import async_session_maker
from chat.models import Message
from auth.models import User
from config import BOT_TOKEN

celery = Celery('tasks', broker='redis://localhost:6379')
celery.config_from_object("tasks.celeryconfig")


async def send_telegram_notification(telegram_id: int, message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"chat_id": telegram_id, "text": message})
        if response.status_code != 200:
            print(f"Ошибка при отправке уведомления: {response.status_code}, {response.text}")


@celery.task
def notify_unread_messages():
    asyncio.run(check_and_notify_unread_messages())


async def check_and_notify_unread_messages():
    async with async_session_maker() as session:
        # Запрос на выборку пользователей с непрочитанными сообщениями
        result = await session.execute(
            select(User)
            .join(Message, Message.receiver_id == User.id)
            .where(Message.read == False, User.telegram_id != None)  # Добавлен фильтр на telegram_id
            .distinct()
        )
        users = result.scalars().all()
        print(f"Найдено {len(users)} пользователей с непрочитанными сообщениями")

        for user in users:
            print(user.username)
            # Получение непрочитанных сообщений
            result = await session.execute(
                select(Message).where(Message.receiver_id == user.id, Message.read == False)
            )
            messages = result.scalars().all()

            # Отправка уведомления пользователю через бота
            if messages:
                unread_count = len(messages)
                message_text = f"У вас {unread_count} непрочитанных сообщений."
                await send_telegram_notification(user.telegram_id, message_text)

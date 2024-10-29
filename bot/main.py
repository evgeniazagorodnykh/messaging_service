import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN
from handlers import get_start, process_email, process_password, Form


async def start():
    """Функция, запускающая работу бота."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher()
    dp.message.register(
        get_start,
        Command(commands=['start', 'run'])
    )

    dp.message.register(process_email, Form.EMAIL_STATE)
    dp.message.register(process_password, Form.PASSWORD_STATE)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())

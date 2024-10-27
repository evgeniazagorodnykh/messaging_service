import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN


async def get_start(message: Message, bot: Bot):
    """Приветствие."""
    await message.answer(
        f'Привет, {message.from_user.first_name}!\n'
        'Я бот, который будет уведомлять тебя о непрочитанных сообщениях.',
        parse_mode='HTML'
    )


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

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())

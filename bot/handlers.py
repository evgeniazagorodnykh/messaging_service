import httpx
from aiogram import Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import APP_URL


class Form(StatesGroup):
    EMAIL_STATE = State()  # Состояние для ввода email
    PASSWORD_STATE = State()  # Состояние для ввода пароля


async def get_start(message: Message, bot: Bot, state: FSMContext):
    """Приветствие."""
    await message.answer(
        f'Привет, {message.from_user.first_name}!\n'
        'Я бот, который будет уведомлять тебя о непрочитанных сообщениях.\n'
        'Для авторизации введите свой email\n',
        parse_mode='HTML'
    )
    await state.set_state(Form.EMAIL_STATE)


async def process_email(message: Message, state: FSMContext):
    """Обработка введенного email и переход к вводу пароля."""
    email = message.text.strip()
    await state.update_data(email=email)  # Сохраняем email в состоянии

    await message.answer('Спасибо! Теперь введи свой пароль.')
    await state.set_state(Form.PASSWORD_STATE)  # Устанавливаем состояние password


async def process_password(message: Message, state: FSMContext):
    """Обработка пароля, отправка данных на API и добавление telegram_id."""
    password = message.text.strip()
    user_data = await state.get_data()  # Получаем email из состояния
    email = user_data.get('email')
    telegram_id = str(message.from_user.id)  # Telegram ID пользователя
    await message.answer(f"email: {email}, password: {password}, telegram_id: {telegram_id}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{APP_URL}users/telegram",
            params={"email": email, "password": password, "telegram_id": telegram_id}
        )

        print(response.text)
    
    if response.status_code == 200:
        await message.answer('Ваш Telegram ID успешно связан с вашим аккаунтом!')
    else:
        await message.answer('Неправильный email или пароль. Пожалуйста, попробуйте снова.')

    await state.clear()
from datetime import datetime
from modules.database.log.log import Log
import traceback

from telegram.ext import (
    ContextTypes
)
from telegram import (
    Update
)


def logger(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:

            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            text = f'{now}: {func.__name__}\n{repr(e)}\n'
            text += traceback.format_exc()
            Log.insert(text)

    return wrapper


def async_logger(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:

            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            text = f'{now}: {func.__name__}\n{repr(e)}\n'
            text += traceback.format_exc()
            Log.insert(text)

    return wrapper


def telegram_logger(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:

            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            text = f'{now}: {func.__name__}\n{repr(e)}\n'
            text += traceback.format_exc()
            Log.insert(text)
            await args[1].bot.send_message(
                chat_id=args[0].effective_chat.id,
                text="Произошла ошибка. Пожалуйста, опишите, что вы делали перед её появлением, и укажите ваши группы. Напишите сюда: @Sarrz0."
            )

    return wrapper

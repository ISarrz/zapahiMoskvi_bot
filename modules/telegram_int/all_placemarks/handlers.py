from modules.telegram_int.constants import *
from telegram import Update
from telegram.ext import CallbackContext
from modules.logger.logger import async_logger

@async_logger
async def all_placemarks_handler(update: Update, context: CallbackContext) -> int:
    text = "Все метки можно посмотреть здесь: http://87.251.78.183/"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=None
    )

    return MAIN_MENU_HANDLER

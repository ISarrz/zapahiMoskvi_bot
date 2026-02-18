from modules.telegram_int.constants import *
from telegram import Update
from telegram.ext import CallbackContext
from modules.logger.logger import async_logger

@async_logger
async def all_placemarks_handler(update: Update, context: CallbackContext) -> int:
    text = ("🗺️ Метки, оставленные Вами и другими пользователями, можно посмотреть на карте проекта здесь — "
            "http://zapahimap.ru/\n\n"
            "<i>На карту попадают геометки, прошедшие модерацию.</i>")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=None,
        parse_mode="HTML"
    )

    return MAIN_MENU_HANDLER

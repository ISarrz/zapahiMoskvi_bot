from modules.telegram_int.constants import *
from telegram import Update
from telegram.ext import CallbackContext

async def about_handler(update: Update, context: CallbackContext) -> int:

    text = ("Привет! Это бот, отслеживающий запахи Москвы. "
    "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
    "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
    "готовым нотам, разбитым на категории.")
    # text = '2'

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=None
    )

    return MAIN_MENU_HANDLER
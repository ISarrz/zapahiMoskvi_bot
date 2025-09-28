from modules.database import *
from modules.config import *
from modules.telegram_int.add_geotag.add_geotag import ConversationHandler_add_geotag
from io import BytesIO
from datetime import datetime
from modules.config.config import get_config_field
from telegram import (
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    CommandHandler
)


async def get_geotags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(telegram_id=update.effective_user.id)
    geotags = Geotag.all()
    for geotag in geotags:
        text = geotag.geotag + "\n" + geotag.about
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def my_geotags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(telegram_id=update.effective_user.id)
    user = User(telegram_id=update.effective_user.id)
    geotags = user.geotags
    if not geotags:
        return
    for geotag in geotags:
        text = geotag.geotag + "\n" + geotag.about
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(telegram_id=update.effective_user.id)
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    User.safe_insert(telegram_id=update.effective_user.id)
    await update.message.reply_text(text="Начальное сообщение")


def main():
    token = get_config_field("telegram_api_token")
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    application.add_handler(CommandHandler('get_geotags', get_geotags))
    application.add_handler(CommandHandler('my_geotags', my_geotags))
    application.add_handler(ConversationHandler_add_geotag, 1)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

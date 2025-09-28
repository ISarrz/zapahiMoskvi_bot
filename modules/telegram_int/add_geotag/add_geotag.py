
from modules.database import Geotag, User

from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text(text="Отправьте геометку")
    User.safe_insert(update.effective_user.id)

    return 0


async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    context.user_data["latitude"] = latitude
    context.user_data["longitude"] = longitude
    await update.message.reply_text(f"Добавьте описание")

    return 1


async def description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    user = User(telegram_id=update.effective_user.id)
    print(context.user_data["latitude"])
    geotag = f"{context.user_data["latitude"]};{context.user_data["longitude"]}"
    user.insert_geotag(geotag=geotag, about=description)

    await update.message.reply_text(f"Ваша геометка добавлена")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_add_geotag = ConversationHandler(
    entry_points=[CommandHandler('add_geotag', start)],

    states={
        0: [MessageHandler(filters.LOCATION, location_handler)],
        1: [MessageHandler(filters.TEXT, description_handler)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

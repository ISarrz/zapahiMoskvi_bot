from modules.database.user.user import User
from io import BytesIO
from modules.database.log.log import Log
from modules.time.time import now_data
from modules.config.config import get_config_field
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from modules.telegram_int.notifications.handlers import send_notifications
from telegram.error import Forbidden, TelegramError
from modules.telegram_int.main_menu import ConversationHandler_main_menu
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
)

from modules.logger.logger import async_logger
from modules.config.config import get_telegram_message
from modules.telegram_int.notifications.handlers import notifications_handler


@async_logger
async def send_logs(context: CallbackContext):
    chat_id = get_config_field("logs_chat_id")
    for log in Log.all():
        bio = BytesIO(log.value.encode("utf-8"))
        bio.name = "log.txt"
        if len(log.value) > 4096:
            await context.bot.send_document(chat_id=chat_id, document=bio)
        else:
            await context.bot.send_message(chat_id=chat_id, text=log.value)
        log.delete()


@async_logger
async def send_reboot_notifications(context: CallbackContext):
    for user in User.all():
        try:
            text = "Проведено техническое обслуживание. Для дальнейшей работы пропишите /start"
            await context.bot.send_message(chat_id=user.telegram_id, text=text)
        except Exception as e:
            pass


async def send_db(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = User(telegram_id=update.effective_user.id)
    if user.role != "admin":
        return

    with open(database_path, "rb") as db_file:
        await context.bot.send_document(
            chat_id=chat_id,
            document=db_file,
            filename="database.db"
        )


@async_logger
async def get_chat_id(update: Update, context: CallbackContext):
    User.safe_insert(telegram_id=update.effective_user.id)
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


@async_logger
async def all_placemarks(update: Update, context: CallbackContext):
    User.safe_insert(telegram_id=update.effective_user.id)
    await update.message.reply_text(text="ССЫЛКА НА КАРТУ")


def main():
    token = get_config_field("telegram_api_token")
    application = ApplicationBuilder().token(token).build()

    application.add_handler(ConversationHandler_main_menu, 1)
    application.add_handler(CallbackQueryHandler(notifications_handler, pattern="настройка напоминаний"), 2)
    application.add_handler(CommandHandler("get_db", send_db))
    job_deque = application.job_queue
    job_deque.run_repeating(send_logs, 20)
    job_deque.run_once(send_reboot_notifications, 0)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


from modules.config.paths import telegram_messages_path, database_path

print(telegram_messages_path)
if __name__ == '__main__':
    main()

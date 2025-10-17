from modules.database.user.user import User
from modules.config import *
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)
from modules.telegram_int.user_placemarks_menu.user_placemarks_menu import ConversationHandler_placemarks_editor
from io import BytesIO
from modules.telegram_int.notifications_editor.notifications_editor import ConversationHandler_notifications_editor
from modules.database.log.log import Log
from modules.time.time import now_data
from modules.config.config import get_config_field
from telegram import (
    Update
)
from modules.telegram_int.main_menu import ConversationHandler_main_menu
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CallbackContext,
    ContextTypes,
    CommandHandler
)
from modules.telegram_int.admin_panel.admin_panel_menu import ConversationHandler_admin_panel


# @async_logger
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


# @async_logger
notifications_states = dict()


async def send_notifications(context: CallbackContext):
    for user in User.all():
        now = now_data()
        weekday = now.weekday()
        hour = now.hour
        if notifications_states.get(str(user.id) + " " + str(weekday) + " " + str(hour)) is None:
            notifications_states[str(user.id) + " " + str(weekday) + " " + str(hour)] = False

        if not user.notifications:
            continue

        for notification in user.notifications:
            if weekday == notification.weekday and hour == int(notification.time.split(":")[0]):
                if not notifications_states[str(user.id) + " " + str(weekday) + " " + str(hour)]:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text="Напоминание",
                        reply_markup=None
                    )
                    notifications_states[str(user.id) + " " + str(weekday) + " " + str(hour)] = True

            else:
                notifications_states[
                    str(user.id) + " " + str(notification.weekday) + " " + str(notification.time.split(":")[0])] = False


# async def get_geotags(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     User.safe_insert(telegram_id=update.effective_user.id)
#     geotags = Geotag.all()
#     for geotag in geotags:
#         text = geotag.geotag + "\n" + geotag.about
#         await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def get_chat_id(update: Update, context: CallbackContext):
    User.safe_insert(telegram_id=update.effective_user.id)
    chat_id = update.effective_chat.id
    await update.message.reply_text(text=str(chat_id))


async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    User.safe_insert(telegram_id=update.effective_user.id)
    await update.message.reply_text(text="Привет! Это бот, отслеживающий запахи Москвы. "
                                         "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
                                         "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
                                         "готовым нотам, разбитым на категории."
                                         "\nЧтобы добавить первый отзыв и геометку, пропишите /placemarks.")


async def all_placemarks(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    User.safe_insert(telegram_id=update.effective_user.id)
    await update.message.reply_text(text="ССЫЛКА НА КАРТУ")


def main():
    token = get_config_field("telegram_api_token")
    application = ApplicationBuilder().token(token).build()

    # application.add_handler(CommandHandler('start', start))
    # application.add_handler(CommandHandler('get_chat_id', get_chat_id))
    # application.add_handler(CommandHandler('all_placemarks', all_placemarks))
    application.add_handler(ConversationHandler_main_menu, 1)
    # application.add_handler(ConversationHandler_notifications_editor, 2)
    # application.add_handler(ConversationHandler_admin_panel, 3)

    job_deque = application.job_queue
    job_deque.run_repeating(send_logs, 20)
    job_deque.run_repeating(send_notifications, 20)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

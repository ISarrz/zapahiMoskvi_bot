from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters, CallbackContext
)

from modules.database.user.notification import Notification
from modules.logger.logger import logger, async_logger
from modules.database.user.user import User

MAX_SHEET_LENGTH = 5
LEFT_ARROW = "←"
RIGHT_ARROW = "→"
BACK_ARROW = "↵"
ADD = "+"
EDIT = "✎"
DELETE = "❌"
SUBMIT = "✓︎"
CANCEL = "⨯"


def get_weekdays_sheet():
    keyboard = [
        [InlineKeyboardButton("Понедельник", callback_data=0)],
        [InlineKeyboardButton("Вторник", callback_data=1)],
        [InlineKeyboardButton("Среда", callback_data=2)],
        [InlineKeyboardButton("Четверг", callback_data=3)],
        [InlineKeyboardButton("Пятница", callback_data=4)],
        [InlineKeyboardButton("Суббота", callback_data=5)],
        [InlineKeyboardButton("Воскресенье", callback_data=6)]
    ]

    return keyboard


@async_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    User.safe_insert(update.effective_chat.id)

    await send_weekdays(update, context)
    return 0


@async_logger
async def send_weekdays(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(get_weekdays_sheet())

    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Уведомления",
                                             reply_markup=reply_markup)

    context.user_data['notifications_message'] = message


@async_logger
async def update_weekdays(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(get_weekdays_sheet())
    message = context.user_data['notifications_message']
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Уведомления",
        reply_markup=reply_markup
    )


@async_logger
async def weekdays_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    context.user_data['weekday'] = income
    await update_time(update, context)
    return 1


async def update_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.user_data['notifications_message']
    sheet = get_time_sheet(User(telegram_id=update.effective_chat.id), context)
    reply_markup = InlineKeyboardMarkup(sheet)
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Уведомления",
        reply_markup=reply_markup
    )


@async_logger
async def time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if "delete" in income:
        income = income.replace("delete ", "")
        notification_id = int(income)
        notification = Notification(id=notification_id)
        notification.delete()

        await update_time(update, context)
        return 1

    elif "add" in income:
        income = income.replace("add ", "").split()
        notification_weekday = int(income[0])
        notification_time = income[1]
        user = User(telegram_id=update.effective_chat.id)
        Notification.insert(user.id, notification_weekday, notification_time)

        await update_time(update, context)
        return 1

    elif income == BACK_ARROW:
        await update_weekdays(update, context)
        return 0

    await update_time(update, context)
    return 1


@logger
def get_time_inline_button(user: User, weekday: int, time):
    notifications = user.notifications
    if not notifications:
        return InlineKeyboardButton(text=time, callback_data="add " + str(weekday) + " " + time)

    for notification in notifications:
        if weekday == notification.weekday and time == notification.time:
            return InlineKeyboardButton(text=time + " " + SUBMIT, callback_data="delete " + str(notification.id))

    return InlineKeyboardButton(text=time, callback_data="add " + str(weekday) + " " + time)


@logger
def get_time_sheet(user: User, context: ContextTypes.DEFAULT_TYPE):
    notifications = user.notifications
    weekday = int(context.user_data['weekday'])
    keyboard = [
        [
            get_time_inline_button(user, weekday, "00:00"),
            get_time_inline_button(user, weekday, "08:00"),
            get_time_inline_button(user, weekday, "16:00"),
        ],
        [
            get_time_inline_button(user, weekday, "01:00"),
            get_time_inline_button(user, weekday, "09:00"),
            get_time_inline_button(user, weekday, "17:00"),
        ],
        [
            get_time_inline_button(user, weekday, "02:00"),
            get_time_inline_button(user, weekday, "10:00"),
            get_time_inline_button(user, weekday, "18:00"),
        ],
        [
            get_time_inline_button(user, weekday, "03:00"),
            get_time_inline_button(user, weekday, "11:00"),
            get_time_inline_button(user, weekday, "19:00"),
        ],
        [
            get_time_inline_button(user, weekday, "04:00"),
            get_time_inline_button(user, weekday, "12:00"),
            get_time_inline_button(user, weekday, "20:00"),
        ],
        [
            get_time_inline_button(user, weekday, "05:00"),
            get_time_inline_button(user, weekday, "13:00"),
            get_time_inline_button(user, weekday, "21:00"),
        ],
        [
            get_time_inline_button(user, weekday, "06:00"),
            get_time_inline_button(user, weekday, "14:00"),
            get_time_inline_button(user, weekday, "22:00"),
        ],
        [
            get_time_inline_button(user, weekday, "07:00"),
            get_time_inline_button(user, weekday, "15:00"),
            get_time_inline_button(user, weekday, "23:00"),
        ], [
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        ]
    ]

    return keyboard


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_notifications_editor = ConversationHandler(
    entry_points=[CommandHandler('notifications', start)],

    states={
        0: [CallbackQueryHandler(weekdays_handler)],
        1: [CallbackQueryHandler(time_handler)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

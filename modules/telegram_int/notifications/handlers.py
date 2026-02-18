from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext
from telegram.error import Forbidden, TelegramError
from modules.database.user.notification import Notification
from modules.logger.logger import logger, async_logger
from modules.database.user.user import User
from modules.telegram_int.constants import WEEKDAYS_HANDLER, HOURS_HANDLER, NOTIFICATION_HANDLER, MAIN_MENU_HANDLER
from modules.config.config import get_telegram_message
from modules.time.time import now_data
from modules.config.config import get_notification_message, set_notification_message
from modules.telegram_int.keyboard import get_main_keyboard
import random



MAX_SHEET_LENGTH = 5
LEFT_ARROW = "←"
RIGHT_ARROW = "→"
BACK_ARROW = "↵"
ADD = "+"
EDIT = "✎"
DELETE = "❌"
SUBMIT = "✓︎"
CANCEL = "⨯"
CLOCK = "⏰"

notifications_states = dict()


@async_logger
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
                    try:
                        text = get_telegram_message("notification")
                        message = await context.bot.send_message(
                            chat_id=user.telegram_id,
                            text=text,
                            reply_markup=None,
                            parse_mode="Markdown"
                        )

                        set_notification_message(user.id , message.id)
                    except Forbidden:
                        pass

                    notifications_states[str(user.id) + " " + str(weekday) + " " + str(hour)] = True

            else:
                notifications_states[
                    str(user.id) + " " + str(notification.weekday) + " " + str(notification.time.split(":")[0])] = False


def get_weekdays_sheet(update: Update, context: CallbackContext):
    user = User(telegram_id=update.effective_user.id)
    user_weekdays = set()
    for notification in user.notifications:
        user_weekdays.add(notification.weekday)

    weekdays_numbers = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]
    keyboard = []

    for i in range(len(weekdays_numbers)):
        if i in user_weekdays:
            keyboard.append([InlineKeyboardButton(f"{weekdays_numbers[i]} {CLOCK}", callback_data=i)])
        else:
            keyboard.append([InlineKeyboardButton(f"{weekdays_numbers[i]} ", callback_data=i)], )

    # Проверяем, были ли изменения
    has_changes = False
    if 'original_notifications' in context.user_data:
        current_notifications = set()
        for notification in user.notifications:
            current_notifications.add((notification.weekday, notification.time))

        has_changes = context.user_data['original_notifications'] != current_notifications

    # Добавляем кнопки управления
    keyboard.append([
        InlineKeyboardButton(text="Каждый день", callback_data="everyday"),
    ])

    # Добавляем кнопку "Очистить" если есть уведомления
    has_notifications = len(user.notifications) > 0
    if has_notifications:
        keyboard.append([
            InlineKeyboardButton(text="Очистить", callback_data="clear_all"),
        ])

    # Показываем кнопку "Подтвердить" только если есть изменения
    if has_changes:
        keyboard.append([
            InlineKeyboardButton(text="Подтвердить", callback_data="confirm"),
        ])

    return keyboard


@async_logger
async def notifications_handler(update: Update, context: CallbackContext):
    User.safe_insert(update.effective_chat.id)
    try:
        user = User(telegram_id=update.effective_user.id)
        message_id = get_notification_message(user.id)
        if message_id:
            await context.bot.edit_message_reply_markup(
                chat_id=update.effective_user.id,
                message_id=message_id,
                reply_markup=None
            )
        set_notification_message(user.id, None)

    except Exception:
        pass

    # Сохраняем исходное состояние уведомлений
    user = User(telegram_id=update.effective_user.id)
    context.user_data['original_notifications'] = set()
    for notification in user.notifications:
        context.user_data['original_notifications'].add((notification.weekday, notification.time))

    await send_weekdays(update, context)
    return WEEKDAYS_HANDLER


@async_logger
async def send_weekdays(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(get_weekdays_sheet(update, context))
    text = get_telegram_message("notifications_settings")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Напоминания",
                                             reply_markup=reply_markup)

    context.user_data['message'] = message


@async_logger
async def update_weekdays(update: Update, context: CallbackContext):
    reply_markup = InlineKeyboardMarkup(get_weekdays_sheet(update, context))
    message = context.user_data['message']
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Уведомления",
        reply_markup=reply_markup
    )


@async_logger
async def weekdays_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == "everyday":
        # Удаляем все существующие уведомления
        user = User(telegram_id=update.effective_chat.id)
        for db_notification in user.notifications:
            notification = Notification(id=db_notification.id)
            notification.delete()

        # Добавляем уведомление на каждый день в 12:00
        for weekday in range(7):
            Notification.insert(user.id, weekday, "12:00")


        await update_weekdays(update, context)
        return WEEKDAYS_HANDLER

    elif income == "clear_all":
        # Удаляем все уведомления
        user = User(telegram_id=update.effective_chat.id)
        for db_notification in user.notifications:
            notification = Notification(id=db_notification.id)
            notification.delete()

        await update_weekdays(update, context)
        return WEEKDAYS_HANDLER

    elif income == "confirm":
        # Отправляем сообщение подтверждения
        user = User(telegram_id=update.effective_chat.id)
        message = context.user_data['message']

        # Удаляем inline-сообщение
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="✅ Напоминания успешно настроены!",
            reply_markup=None
        )

        return MAIN_MENU_HANDLER

    context.user_data['weekday'] = income
    await update_time(update, context)
    return HOURS_HANDLER


async def update_time(update: Update, context: CallbackContext):
    message = context.user_data['message']
    sheet = get_time_sheet(User(telegram_id=update.effective_chat.id), context)
    reply_markup = InlineKeyboardMarkup(sheet)
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Уведомления",
        reply_markup=reply_markup
    )


@async_logger
async def time_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if "delete" in income:
        income = income.replace("delete ", "")
        notification_id = int(income)
        notification = Notification(id=notification_id)
        notification.delete()

        await update_time(update, context)
        return HOURS_HANDLER

    elif "add" in income:
        income = income.replace("add ", "").split()
        notification_weekday = int(income[0])
        notification_time = income[1]
        user = User(telegram_id=update.effective_chat.id)
        Notification.insert(user.id, notification_weekday, notification_time)

        await update_time(update, context)
        return HOURS_HANDLER

    elif income == BACK_ARROW:
        await update_weekdays(update, context)
        return WEEKDAYS_HANDLER

    await update_time(update, context)
    return WEEKDAYS_HANDLER


@logger
def get_time_inline_button(user: User, weekday: int, time):
    notifications = user.notifications
    if not notifications:
        return InlineKeyboardButton(text=time, callback_data="add " + str(weekday) + " " + time)

    for notification in notifications:
        if weekday == notification.weekday and time == notification.time:
            return InlineKeyboardButton(text=time + " " + CLOCK, callback_data="delete " + str(notification.id))

    return InlineKeyboardButton(text=time, callback_data="add " + str(weekday) + " " + time)


@logger
def get_time_sheet(user: User, context: CallbackContext):
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

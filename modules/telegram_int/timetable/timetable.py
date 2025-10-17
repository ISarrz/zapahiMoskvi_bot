from modules.time import *
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
    filters
)
from modules.database import User
from modules.logger.logger import async_logger, telegram_logger


LEFT_ARROW = "←"
RIGHT_ARROW = "→"
BACK_ARROW = "↵"
ADD = "+"
EDIT = "edit"
DELETE = "❌"
SUBMIT = "✓︎"
CANCEL = "⨯"


def get_previous_week_sheet(user: User):
    weekdays = get_previous_week_string_weekdays()
    days = get_previous_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_current_week_sheet(user: User):
    weekdays = get_current_week_string_weekdays()
    days = get_current_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_week_sheet(days, weekdays, user):
    timetables = dict()
    keyboard = []
    for i in range(len(days)):
        timetable = user.get_date_timetable(days[i])
        if not timetable or not timetable.image or not timetable.text:
            continue

        timetables[days[i]] = timetable

        keyboard.append([InlineKeyboardButton(text=weekdays[i], callback_data=days[i])])

    if not keyboard:
        return None

    return {
        "keyboard": keyboard,
        "timetables": timetables
    }


def get_next_week_sheet(user: User):
    weekdays = get_next_week_string_weekdays()
    days = get_next_week_string_days()

    return get_week_sheet(days, weekdays, user)


def get_sheets(user: User):
    sheets = []
    if get_previous_week_sheet(user):
        sheet = get_previous_week_sheet(user)
        sheet["text"] = "Предыдущая неделя"
        sheets.append(sheet)

    if get_current_week_sheet(user):
        sheet = get_current_week_sheet(user)
        sheet["text"] = "Текущая неделя"
        sheets.append(sheet)

    if get_next_week_sheet(user):
        sheet = get_next_week_sheet(user)
        sheet["text"] = "Следующая неделя"
        sheets.append(sheet)

    if len(sheets) > 1:
        for sheet in sheets:
            keyboard = sheet["keyboard"]
            keyboard.append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])
            sheet["keyboard"] = keyboard

    for sheet in sheets:
        keyboard = sheet["keyboard"]
        sheet["reply_markup"] = InlineKeyboardMarkup(keyboard)

    return sheets


@telegram_logger
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = get_statistics_field("timetable_count")
    set_statistics_field("timetable_count", count + 1)

    User.safe_insert(update.effective_chat.id)
    weeks = [sheet["text"] for sheet in get_sheets(User(telegram_id=update.effective_chat.id))]
    if "Текущая неделя" in weeks:
        context.user_data['timetable_sheet'] = weeks.index("Текущая неделя")

    elif "Следующая неделя" in weeks:
        context.user_data['timetable_sheet'] = weeks.index("Следующая неделя")

    else:
        context.user_data['timetable_sheet'] = 0

    await send_week(update, context)
    return 0


@telegram_logger
async def week_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data['timetable_sheet'] -= 1
        sheets = context.user_data['timetable_sheets']
        context.user_data['timetable_sheet'] += len(sheets)
        context.user_data['timetable_sheet'] %= len(sheets)

        await update_week(update, context)

        return 0

    elif income == RIGHT_ARROW:
        context.user_data['timetable_sheet'] += 1
        sheets = context.user_data['timetable_sheets']
        context.user_data['timetable_sheet'] %= len(sheets)

        await update_week(update, context)

        return 0

    else:
        await send_timetable(update, context, income)
        return ConversationHandler.END


async def update_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['timetable_sheets'] = get_sheets(User(telegram_id=update.effective_chat.id))

    if not context.user_data['timetable_sheets']:
        message = await update.message.reply_text(text="Расписания нет", reply_markup=None)
        return

    sheets = context.user_data['timetable_sheets']
    sheet = sheets[context.user_data['timetable_sheet']]

    message = context.user_data['timetable_message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=sheet["text"],
        reply_markup=sheet["reply_markup"]
    )


@telegram_logger
async def send_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['timetable_sheets'] = get_sheets(User(telegram_id=update.effective_chat.id))

    if not context.user_data['timetable_sheets']:
        message = await update.message.reply_text(text="Расписания нет", reply_markup=None)
        return

    sheets = context.user_data['timetable_sheets']
    sheet = sheets[context.user_data['timetable_sheet']]

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=sheet["text"],
        reply_markup=sheet["reply_markup"]
    )

    context.user_data['timetable_message'] = message


@telegram_logger
async def send_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE, date: str):
    sheets = context.user_data['timetable_sheets']
    sheet = sheets[context.user_data['timetable_sheet']]
    timetable = sheet["timetables"][date]
    user = User(telegram_id=update.effective_chat.id)

    if user.settings.mode == "image":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=timetable.image
        )

    elif user.settings.mode == "text":
        await context.bot.send_message(chat_id=update.effective_chat.id, text=timetable.text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


ConversationHandler_timetable = ConversationHandler(
    entry_points=[CommandHandler('timetable', start)],

    states={
        0: [CallbackQueryHandler(week_menu)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

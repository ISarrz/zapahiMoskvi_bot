from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from modules.database.user.user import User
from modules.telegram_int.user_placemarks_menu.placemark_selector.sheets_generators import \
    placemark_selector_get_placemarks_sheets


async def placemark_selector_send_placemarks_menu(update: Update, context: CallbackContext):
    sheets = placemark_selector_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
    sheet = sheets[context.user_data['placemark_sheet']]
    reply_markup = InlineKeyboardMarkup(sheet)

    if sheets and len(sheets) > 1:
        text = "Метки №" + str(context.user_data['placemark_sheet'] + 1)
    elif not sheet:
        text = "Меток нет"
    else:
        text = "Метки"

    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=text,
                                             reply_markup=reply_markup)

    context.user_data['placemark_message'] = message


async def placemark_selector_update_placemarks_menu(update: Update, context: CallbackContext):
    sheets = placemark_selector_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
    sheet = sheets[context.user_data['placemark_sheet']]
    reply_markup = InlineKeyboardMarkup(sheet)
    if len(sheets) > 1:
        text = "Метки №" + str(context.user_data['placemark_sheet'] + 1)
    else:
        text = "Метки"
    message = context.user_data['placemark_message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

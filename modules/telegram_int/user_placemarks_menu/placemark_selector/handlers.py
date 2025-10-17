from telegram import Update
from telegram.ext import CallbackContext
from modules.logger.logger import async_logger
from modules.database.user.user import User

from modules.telegram_int.user_placemarks_menu.constants import *
from modules.telegram_int.user_placemarks_menu.placemark_selector.sheets_generators import \
    placemark_selector_get_placemarks_sheets
from modules.telegram_int.user_placemarks_menu.placemark_selector.messages_interactions import \
    placemark_selector_update_placemarks_menu
from modules.telegram_int.user_placemarks_menu.placemark_editor.messages_interactions import \
    placemark_editor_update_placemark_info_menu


@async_logger
async def placemarks_selector_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data['placemark_sheet'] -= 1
        sheets = placemark_selector_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
        context.user_data['placemark_sheet'] += len(sheets)
        context.user_data['placemark_sheet'] %= len(sheets)

        await placemark_selector_update_placemarks_menu(update, context)

        return PLACEMARK_SELECTOR_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data['placemark_sheet'] += 1
        sheets = placemark_selector_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
        context.user_data['placemark_sheet'] %= len(sheets)

        await placemark_selector_update_placemarks_menu(update, context)

        return PLACEMARK_SELECTOR_HANDLER

    elif income == ADD:
        context.user_data["tags"] = []
        context.user_data['categories_sheet'] = 0
        context.user_data['tags_sheet'] = 0

        message = context.user_data['placemark_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Отправьте локацию",
            reply_markup=None
        )
        return PLACEMARK_INSERTER_LOCATION_HANDLER

    else:
        context.user_data['selected_placemark_id'] = int(income)
        await placemark_editor_update_placemark_info_menu(update, context)
        return PLACEMARK_EDITOR_HANDLER

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from modules.logger.logger import async_logger

from modules.telegram_int.admin_panel.constants import *
from modules.telegram_int.admin_panel.approved_placemarks.sheets_generators import \
    approved_placemarks_get_placemarks_sheets
from modules.telegram_int.admin_panel.approved_placemarks.messages_interactions import (
    approved_placemarks_update_placemark_info,
    approved_placemarks_update_placemarks_menu
)
from modules.telegram_int.admin_panel.mode_selector.messages_interactions import (
mode_selector_update_menu
)


@async_logger
async def approved_placemarks_selector_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data['approved_placemark_sheet'] -= 1
        sheets = approved_placemarks_get_placemarks_sheets()
        context.user_data['approved_placemark_sheet'] += len(sheets)
        context.user_data['approved_placemark_sheet'] %= len(sheets)

        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data['approved_placemark_sheet'] += 1
        sheets = approved_placemarks_get_placemarks_sheets()
        context.user_data['approved_placemark_sheet'] %= len(sheets)

        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

    elif income == BACK_ARROW:
        await mode_selector_update_menu(update, context)

        return MODE_SELECTOR_HANDLER
    else:
        context.user_data['selected_placemark_id'] = int(income)
        await approved_placemarks_update_placemark_info(update, context)

        return APPROVED_PLACEMARKS_PLACEMARK_INFO_HANDLER


@async_logger
async def approved_placemarks_placemark_info_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

    return ConversationHandler.END

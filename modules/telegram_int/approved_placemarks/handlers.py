from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from modules.logger.logger import async_logger
from modules.database.user.user import User
from modules.telegram_int.constants import *
from modules.telegram_int.approved_placemarks.sheets_generators import \
    approved_placemarks_get_placemarks_sheets
from modules.telegram_int.approved_placemarks.messages_interactions import (
    approved_placemarks_update_placemark_info,
    approved_placemarks_update_placemarks_menu,
    approved_placemarks_send_placemarks_menu,
    approved_placemarks_update_reject_menu
)
from modules.database.placemark.placemark import Placemark


@async_logger
async def approved_placemarks_handler(update: Update, context: CallbackContext):
    user = User(telegram_id=update.effective_user.id)
    if user.role != "admin":
        text = ("Привет! Это бот, отслеживающий запахи Москвы. "
                "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
                "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
                "готовым нотам, разбитым на категории."
                "\n\nЧтобы добавить первый ольфакторный отзыв, нажмите кнопку «Добавить метку».")

        await update.message.reply_text(
            text=text
        )

        return MAIN_MENU_HANDLER

    context.user_data['approved_placemarks_sheet'] = 0
    await approved_placemarks_send_placemarks_menu(update, context)

    return APPROVED_PLACEMARKS_HANDLER


@async_logger
async def approved_placemarks_selector_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data['approved_placemarks_sheet'] -= 1
        sheets = approved_placemarks_get_placemarks_sheets()
        context.user_data['approved_placemarks_sheet'] += len(sheets)
        context.user_data['approved_placemarks_sheet'] %= len(sheets)

        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data['approved_placemarks_sheet'] += 1
        sheets = approved_placemarks_get_placemarks_sheets()
        context.user_data['approved_placemarks_sheet'] %= len(sheets)

        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

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

    elif income == "reject":
        await approved_placemarks_update_reject_menu(update, context)

        return APPROVED_PLACEMARKS_REJECT_HANDLER

    return ConversationHandler.END


@async_logger
async def approved_placemarks_reject_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        placemark.reject()

        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

    elif income == CANCEL:
        await approved_placemarks_update_placemark_info(update, context)

        return APPROVED_PLACEMARKS_PLACEMARK_INFO_HANDLER

    return ConversationHandler.END

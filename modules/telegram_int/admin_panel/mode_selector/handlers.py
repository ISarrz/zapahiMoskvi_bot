from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from modules.logger.logger import async_logger
from modules.telegram_int.admin_panel.constants import *
from modules.telegram_int.admin_panel.approved_placemarks.messages_interactions import (
    approved_placemarks_update_placemarks_menu
)
from modules.telegram_int.admin_panel.insert_category_and_tag.messages_interactions import (
insert_category_and_tag_update_categories_menu
)
from modules.telegram_int.admin_panel.new_placemarks.messages_interactions import new_placemarks_update_placemarks_menu
from modules.telegram_int.admin_panel.new_tags.messages_interactions import new_tags_update_tags_menu
@async_logger
async def mode_selector_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == "approved placemarks":
        context.user_data["approved_placemarks_sheet"] = 0
        await approved_placemarks_update_placemarks_menu(update, context)

        return APPROVED_PLACEMARKS_HANDLER

    elif income == "add categories and tags":
        context.user_data['categories_sheet'] = 0
        await insert_category_and_tag_update_categories_menu(update, context)
        return INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER

    elif income == "new placemarks":
        context.user_data['new_placemarks_sheet'] = 0
        await new_placemarks_update_placemarks_menu(update, context)
        return NEW_PLACEMARKS_HANDLER

    elif income == "new tags":
        context.user_data['tags_sheet'] = 0
        await new_tags_update_tags_menu(update, context)

        return NEW_TAGS_TAGS_MENU_HANDLER

    return ConversationHandler.END

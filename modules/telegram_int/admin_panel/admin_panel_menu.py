from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from modules.logger.logger import async_logger
from modules.database.user.user import User

from modules.telegram_int.admin_panel.constants import *
from modules.telegram_int.admin_panel.mode_selector.messages_interactions import mode_selector_send_menu
from modules.telegram_int.admin_panel.mode_selector.handlers import mode_selector_handler
from modules.telegram_int.admin_panel.approved_placemarks.handlers import (
    approved_placemarks_selector_handler,
    approved_placemarks_placemark_info_handler
)

from modules.telegram_int.admin_panel.insert_category_and_tag.handlers import (
    insert_category_and_tag_categories_handler,
    insert_category_and_tag_insert_category_handler,
    insert_category_and_tag_edit_category_handler,
    insert_category_and_tag_delete_category_handler,
    insert_category_and_tag_tags_handler,
    insert_category_and_tag_insert_tag_handler,
    insert_category_and_tag_tag_menu_handler,
    insert_category_and_tag_edit_tag_handler,
    insert_category_and_tag_delete_tag_handler
)

from modules.telegram_int.admin_panel.new_tags.handlers import (
    new_tags_tags_menu_handler,
    new_tags_tag_menu_handler,
    new_tags_tag_edit_handler,
    new_tags_delete_tag_handler,
    new_tags_approve_tag_handler
)

from modules.telegram_int.admin_panel.new_placemarks.handlers import (
    new_placemarks_selector_handler,
    new_placemarks_placemark_menu_handler,
    new_placemarks_placemark_approve_handler,
    new_placemarks_placemark_edit_handler,
    new_placemarks_placemark_edit_location_handler,
    new_placemarks_placemark_edit_address_handler,
    new_placemarks_placemark_edit_description_handler,
    new_placemarks_placemark_delete_handler,
    new_placemarks_tags_menu_handler,
    new_placemarks_tag_menu_handler,
    new_placemarks_tag_edit_handler,
    new_placemarks_delete_tag_handler,
    new_placemarks_approve_tag_handler
)


@async_logger
async def start(update: Update, context: CallbackContext):
    User.safe_insert(update.effective_user.id)
    user = User(telegram_id=int(update.effective_user.id))
    if user.role != "admin":
        await update.message.reply_text(text="Доступ запрещен")
        return ConversationHandler.END

    await mode_selector_send_menu(update, context)

    return MODE_SELECTOR_HANDLER


async def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


ConversationHandler_admin_panel = ConversationHandler(
    entry_points=[CommandHandler('admin_panel', start)],

    states={
        MODE_SELECTOR_HANDLER: [CallbackQueryHandler(mode_selector_handler)],
        APPROVED_PLACEMARKS_HANDLER: [CallbackQueryHandler(approved_placemarks_selector_handler)],
        APPROVED_PLACEMARKS_PLACEMARK_INFO_HANDLER: [CallbackQueryHandler(approved_placemarks_placemark_info_handler)],
        INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER: [
            CallbackQueryHandler(insert_category_and_tag_categories_handler)],
        INSERT_CATEGORY_AND_TAG_INSERT_CATEGORY_MENU_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, insert_category_and_tag_insert_category_handler)],
        INSERT_CATEGORY_AND_TAG_EDIT_CATEGORY_MENU_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, insert_category_and_tag_edit_category_handler)],
        INSERT_CATEGORY_AND_TAG_DELETE_CATEGORY_MENU_HANDLER: [
            CallbackQueryHandler(insert_category_and_tag_delete_category_handler)],
        INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER: [CallbackQueryHandler(insert_category_and_tag_tags_handler)],
        INSERT_CATEGORY_AND_TAG_INSERT_TAG_MENU_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, insert_category_and_tag_insert_tag_handler)],
        INSERT_CATEGORY_AND_TAG_TAG_MENU_HANDLER: [CallbackQueryHandler(insert_category_and_tag_tag_menu_handler)],
        INSERT_CATEGORY_AND_TAG_EDIT_TAG_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, insert_category_and_tag_edit_tag_handler)],
        INSERT_CATEGORY_AND_TAG_DELETE_TAG_MENU_HANDLER: [
            CallbackQueryHandler(insert_category_and_tag_delete_tag_handler)],
        NEW_TAGS_TAGS_MENU_HANDLER: [
            CallbackQueryHandler(new_tags_tags_menu_handler)],
        NEW_TAGS_TAG_MENU_HANDLER: [
            CallbackQueryHandler(new_tags_tag_menu_handler)],
        NEW_TAGS_TAG_EDIT_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, new_tags_tag_edit_handler)],

        NEW_TAGS_TAG_DELETE_HANDLER: [
            CallbackQueryHandler(new_tags_delete_tag_handler)],
        NEW_TAGS_TAG_APPROVE_HANDLER: [
            CallbackQueryHandler(new_tags_approve_tag_handler)],

        NEW_PLACEMARKS_HANDLER: [
            CallbackQueryHandler(new_placemarks_selector_handler)],
        NEW_PLACEMARKS_PLACEMARK_MENU_HANDLER: [
            CallbackQueryHandler(new_placemarks_placemark_menu_handler)],
        NEW_PLACEMARKS_PLACEMARK_APPROVE_HANDLER: [
            CallbackQueryHandler(new_placemarks_placemark_approve_handler)],
        NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER: [
            CallbackQueryHandler(new_placemarks_placemark_edit_handler)],

        NEW_PLACEMARKS_PLACEMARK_EDIT_GEOTAG_HANDLER: [
            MessageHandler(filters.LOCATION, new_placemarks_placemark_edit_location_handler)],

        NEW_PLACEMARKS_PLACEMARK_EDIT_ADDRESS_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, new_placemarks_placemark_edit_address_handler)],

        NEW_PLACEMARKS_PLACEMARK_EDIT_DESCRIPTION_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, new_placemarks_placemark_edit_description_handler)],

        NEW_PLACEMARKS_PLACEMARK_DELETE_HANDLER: [
            CallbackQueryHandler(new_placemarks_placemark_delete_handler)],

        NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER: [
            CallbackQueryHandler(new_placemarks_tags_menu_handler)],

        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER: [
            CallbackQueryHandler(new_placemarks_tag_menu_handler)],

        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_EDIT_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, new_placemarks_tag_edit_handler)],

        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_DELETE_HANDLER: [
            CallbackQueryHandler(new_placemarks_delete_tag_handler)],

        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_APPROVE_HANDLER: [
            CallbackQueryHandler(new_placemarks_approve_tag_handler)],

        # PLACEMARK_SELECTOR_HANDLER: [CallbackQueryHandler(placemarks_selector_handler)],
        # # PLACEMARKS_EDITOR_HANDLER: [CallbackQueryHandler(edit_placemark_menu)],
        # # DELETE_PLACEMARKS_MENU: [CallbackQueryHandler(delete_placemark_menu)],
        # # UPDATE_MENU: [CallbackQueryHandler(update_menu_handler)],
        # PLACEMARK_EDITOR_HANDLER: [CallbackQueryHandler(placemark_editor_handler)],
        # PLACEMARK_EDITOR_EDIT_MENU_HANDLER: [CallbackQueryHandler(placemark_editor_placemark_edit_menu_handler)],
        # PLACEMARK_EDITOR_DELETE_HANDLER: [CallbackQueryHandler(placemark_editor_delete_menu_handler)],
        # PLACEMARK_EDITOR_TAGS_HANDLER: [CallbackQueryHandler(placemark_editor_tags_handler)],
        # PLACEMARK_EDITOR_CATEGORIES_HANDLER: [CallbackQueryHandler(placemark_editor_categories_handler)],
        # # DESCRIPTION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_input)],
        # PLACEMARK_EDITOR_ADDRESS_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_editor_placemark_edit_address_handler)],
        # PLACEMARK_EDITOR_DESCRIPTION_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_editor_placemark_edit_description_handler)],
        # PLACEMARK_EDITOR_LOCATION_HANDLER: [MessageHandler(filters.LOCATION & ~filters.COMMAND, placemark_editor_placemark_edit_location_handler)],
        # PLACEMARK_EDITOR_INSERT_TAG_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_editor_insert_tag_handler)],
        #
        # PLACEMARK_INSERTER_LOCATION_HANDLER: [MessageHandler(filters.LOCATION, placemark_inserter_location_handler)],
        # PLACEMARK_INSERTER_DESCRIPTION_HANDLER: [
        #     MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_inserter_description_handler)
        # ],
        # PLACEMARK_INSERTER_CATEGORIES_HANDLER: [CallbackQueryHandler(placemark_inserter_categories_handler)],
        # PLACEMARK_INSERTER_TAGS_HANDLER: [CallbackQueryHandler(placemark_inserter_tags_handler)],
        # # TAGS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, tags_input)],
        # # PLACEMARK_INSERTER_INSERT_TAG_HANDLER: [
        # #     MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_inserter_insert_tag_handler)],
        # # LATITUDE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, latitude_input)],
        # # LONGITUDE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, longitude_input)],
        # # ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_input)],
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

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

from modules.telegram_int.user_placemarks_menu.constants import *
from modules.telegram_int.user_placemarks_menu.placemark_selector.messages_interactions import \
    placemark_selector_send_placemarks_menu
from modules.telegram_int.user_placemarks_menu.placemark_selector.handlers import placemarks_selector_handler
from modules.telegram_int.user_placemarks_menu.placemark_inserter.handlers import (
    placemark_inserter_location_handler,
    placemark_inserter_tags_handler,
    placemark_inserter_categories_handler,
    placemark_inserter_description_handler,
    placemark_inserter_insert_tag_handler,

)
from modules.telegram_int.user_placemarks_menu.placemark_editor.handlers import (
placemark_editor_handler,
placemark_editor_placemark_edit_menu_handler,
placemark_editor_placemark_edit_address_handler,
placemark_editor_placemark_edit_location_handler,
placemark_editor_placemark_edit_description_handler,
placemark_editor_categories_handler,
placemark_editor_tags_handler,
placemark_editor_insert_tag_handler,
placemark_editor_delete_menu_handler,


)


@async_logger
async def start(update: Update, context: CallbackContext):
    User.safe_insert(update.effective_chat.id)

    context.user_data['placemark_sheet'] = 0

    await placemark_selector_send_placemarks_menu(update, context)
    return PLACEMARK_SELECTOR_HANDLER


async def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


ConversationHandler_placemarks_editor = ConversationHandler(
    entry_points=[CommandHandler('placemarks', start)],

    states={
        PLACEMARK_SELECTOR_HANDLER: [CallbackQueryHandler(placemarks_selector_handler)],
        PLACEMARK_EDITOR_HANDLER: [CallbackQueryHandler(placemark_editor_handler)],
        PLACEMARK_EDITOR_EDIT_MENU_HANDLER: [CallbackQueryHandler(placemark_editor_placemark_edit_menu_handler)],
        PLACEMARK_EDITOR_DELETE_HANDLER: [CallbackQueryHandler(placemark_editor_delete_menu_handler)],
        PLACEMARK_EDITOR_TAGS_HANDLER: [CallbackQueryHandler(placemark_editor_tags_handler)],
        PLACEMARK_EDITOR_CATEGORIES_HANDLER: [CallbackQueryHandler(placemark_editor_categories_handler)],
        PLACEMARK_EDITOR_ADDRESS_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_editor_placemark_edit_address_handler)],
        PLACEMARK_EDITOR_DESCRIPTION_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_editor_placemark_edit_description_handler)],
        PLACEMARK_EDITOR_LOCATION_HANDLER: [MessageHandler(filters.LOCATION & ~filters.COMMAND, placemark_editor_placemark_edit_location_handler)],
        PLACEMARK_EDITOR_INSERT_TAG_HANDLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_editor_insert_tag_handler)],

        PLACEMARK_INSERTER_LOCATION_HANDLER: [MessageHandler(filters.LOCATION, placemark_inserter_location_handler)],
        PLACEMARK_INSERTER_DESCRIPTION_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_inserter_description_handler)
        ],
        PLACEMARK_INSERTER_CATEGORIES_HANDLER: [CallbackQueryHandler(placemark_inserter_categories_handler)],
        PLACEMARK_INSERTER_TAGS_HANDLER: [CallbackQueryHandler(placemark_inserter_tags_handler)],

        PLACEMARK_INSERTER_INSERT_TAG_HANDLER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, placemark_inserter_insert_tag_handler)]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

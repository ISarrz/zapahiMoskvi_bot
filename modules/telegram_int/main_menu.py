from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup

from modules.logger.logger import async_logger
from modules.database.user.user import User

from modules.telegram_int.constants import *
from modules.telegram_int.about.handlers import about_handler
from modules.telegram_int.all_placemarks.handlers import all_placemarks_handler
from modules.telegram_int.insert_placemark.handlers import (
    insert_placemark_handler,
    insert_placemark_location_handler,
    insert_placemark_description_handler,
    insert_placemark_categories_handler,
    insert_placemark_tags_handler,
    insert_placemark_insert_tag_handler
)
from modules.telegram_int.notifications.handlers import (
    time_handler,
    weekdays_handler,
    notifications_handler
)

from modules.telegram_int.edit_placemark.handlers import (
    edit_placemark_handler,
    placemarks_selector_handler,
    placemark_editor_handler,
    placemark_editor_placemark_edit_menu_handler,
    placemark_editor_placemark_edit_address_handler,
    placemark_editor_placemark_edit_location_handler,
    placemark_editor_placemark_edit_description_handler,
    placemark_editor_categories_handler,
    placemark_editor_tags_handler,
    placemark_editor_insert_tag_handler,
    placemark_editor_delete_menu_handler
)


@async_logger
async def start(update: Update, context: CallbackContext):
    User.safe_insert(update.effective_user.id)
    user = User(telegram_id=int(update.effective_user.id))
    text = ("Привет! Это бот, отслеживающий запахи Москвы. "
            "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
            "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
            "готовым нотам, разбитым на категории."
            "\n\nЧтобы добавить первый ольфакторный отзыв, нажмите кнопку «Добавить метку».")

    reply_keyboard = [
        ["Добавить метку", "Все метки"],
        ["Мои метки", "Напоминания"],
        ["О нас"],
    ]

    # if user.role == "admin":
    #     reply_keyboard.append(["Новые метки", "Категории и теги"])

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, input_field_placeholder="Выберите раздел"
        ),
    )

    return MAIN_MENU_HANDLER


async def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


COMMON_HANDLERS = [
    MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
    MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
    MessageHandler(filters.Regex("(?i)^(Мои метки)$"), edit_placemark_handler),
    MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
    MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
    # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
    # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
]
TEXT_FILTER = ~filters.Regex(
    "(?i)^(Добавить метку|Все метки|Мои метки|Напоминания|О нас|Новые метки|Категории и теги)$")

ConversationHandler_main_menu = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        MAIN_MENU_HANDLER: COMMON_HANDLERS,

        PLACEMARK_INSERTER_LOCATION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.LOCATION, insert_placemark_location_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        PLACEMARK_INSERTER_DESCRIPTION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER,
                           insert_placemark_description_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        PLACEMARK_INSERTER_CATEGORIES_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(insert_placemark_categories_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        PLACEMARK_INSERTER_TAGS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(insert_placemark_tags_handler),
        ],
        PLACEMARK_INSERTER_INSERT_TAG_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER,
                           insert_placemark_insert_tag_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        WEEKDAYS_HANDLER: COMMON_HANDLERS + [

            CallbackQueryHandler(weekdays_handler)
        ],
        HOURS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(time_handler)
        ],

        PLACEMARK_SELECTOR_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(placemarks_selector_handler)
        ],
        PLACEMARK_EDITOR_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(placemark_editor_handler)
        ],
        PLACEMARK_EDITOR_EDIT_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(placemark_editor_placemark_edit_menu_handler)
        ],
        PLACEMARK_EDITOR_ADDRESS_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, placemark_editor_placemark_edit_address_handler)
        ],
        PLACEMARK_EDITOR_LOCATION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.LOCATION, placemark_editor_placemark_edit_location_handler)
        ],
        PLACEMARK_EDITOR_DESCRIPTION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, placemark_editor_placemark_edit_description_handler)
        ],
        PLACEMARK_EDITOR_CATEGORIES_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(placemark_editor_categories_handler)
        ],
        PLACEMARK_EDITOR_TAGS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(placemark_editor_tags_handler)
        ],
        PLACEMARK_EDITOR_INSERT_TAG_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, placemark_editor_insert_tag_handler)
        ],
        PLACEMARK_EDITOR_DELETE_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(placemark_editor_delete_menu_handler)
        ]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram import ReplyKeyboardMarkup, Update

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

from modules.telegram_int.edit_placemarks.handlers import (
    edit_placemarks_handler,
    edit_placemarks_placemarks_selector_handler,
    edit_placemarks_menu_handler,
    edit_placemarks_placemark_edit_menu_handler,
    edit_placemarks_placemark_edit_address_handler,
    edit_placemarks_placemark_edit_location_handler,
    edit_placemarks_placemark_edit_description_handler,
    edit_placemarks_categories_handler,
    edit_placemarks_tags_handler,
    edit_placemarks_insert_tag_handler,
    edit_placemarks_delete_menu_handler
)

from modules.telegram_int.new_placemarks.handlers import (
    new_placemarks_handler,
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
    new_placemarks_approve_tag_handler,

)
from modules.telegram_int.categories_and_tags.handlers import (
    categories_and_tags_handler,
    categories_and_tags_categories_handler,
    categories_and_tags_insert_category_handler,
    categories_and_tags_edit_category_handler,
    categories_and_tags_delete_category_handler,
    categories_and_tags_tags_handler,
    categories_and_tags_insert_tag_handler,
    categories_and_tags_tag_menu_handler,
    categories_and_tags_edit_tag_handler,
    categories_and_tags_delete_tag_handler,

)

from modules.telegram_int.approved_placemarks.handlers import (
    approved_placemarks_handler,
    approved_placemarks_selector_handler,
    approved_placemarks_placemark_info_handler
)

jobs = {}

from modules.telegram_int.notifications.handlers import send_notifications


@async_logger
async def start(update: Update, context: CallbackContext):
    User.safe_insert(update.effective_user.id)
    user = User(telegram_id=int(update.effective_user.id))
    text = ("Привет! Это бот, отслеживающий запахи Москвы. "
            "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
            "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
            "готовым нотам, разбитым на категории."
            "\n\nЧтобы добавить первый ольфакторный отзыв, нажмите кнопку «Добавить метку».")

    chat_id = update.effective_chat.id

    if chat_id in jobs:
        jobs[chat_id].schedule_removal()

    job = context.job_queue.run_repeating(
        send_notifications,
        interval=60,
        first=0,
        chat_id=chat_id
    )

    jobs[chat_id] = job

    reply_keyboard = [
        ["Добавить метку", "Все метки"],
        ["Мои метки", "Напоминания"],
        ["О нас"],
    ]

    if user.role == "admin":
        reply_keyboard.append(["Новые метки", "Категории и теги", "Принятые метки"])

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
    MessageHandler(filters.Regex("(?i)^(Мои метки)$"), edit_placemarks_handler),
    MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
    MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
    MessageHandler(filters.Regex("(?i)^(Новые метки)$"), new_placemarks_handler),
    MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), categories_and_tags_handler),
    MessageHandler(filters.Regex("(?i)^(Принятые метки)$"), approved_placemarks_handler),
]
TEXT_FILTER = ~filters.Regex(
    "(?i)^(Добавить метку|Все метки|Мои метки|Напоминания|О нас|Новые метки|Категории и теги)|Принятые метки$")

ConversationHandler_main_menu = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        MAIN_MENU_HANDLER: COMMON_HANDLERS,
        NOTIFICATION_HANDLER: [CallbackQueryHandler(notifications_handler, pattern="настройка напоминаний")],
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

        EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(edit_placemarks_placemarks_selector_handler)
        ],
        EDIT_PLACEMARKS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(edit_placemarks_menu_handler)
        ],
        EDIT_PLACEMARKS_EDIT_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(edit_placemarks_placemark_edit_menu_handler)
        ],
        EDIT_PLACEMARKS_ADDRESS_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, edit_placemarks_placemark_edit_address_handler)
        ],
        EDIT_PLACEMARKS_LOCATION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.LOCATION, edit_placemarks_placemark_edit_location_handler)
        ],
        EDIT_PLACEMARKS_DESCRIPTION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, edit_placemarks_placemark_edit_description_handler)
        ],
        EDIT_PLACEMARKS_CATEGORIES_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(edit_placemarks_categories_handler)
        ],
        EDIT_PLACEMARKS_TAGS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(edit_placemarks_tags_handler)
        ],
        EDIT_PLACEMARKS_INSERT_TAG_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, edit_placemarks_insert_tag_handler)
        ],
        EDIT_PLACEMARKS_DELETE_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(edit_placemarks_delete_menu_handler)
        ],
        NEW_PLACEMARKS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_selector_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_placemark_menu_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_APPROVE_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_placemark_approve_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_placemark_edit_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_EDIT_GEOTAG_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.LOCATION, new_placemarks_placemark_edit_location_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_EDIT_ADDRESS_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, new_placemarks_placemark_edit_address_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_EDIT_DESCRIPTION_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, new_placemarks_placemark_edit_description_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_DELETE_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_placemark_delete_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_tags_menu_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_tag_menu_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_EDIT_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, new_placemarks_tag_edit_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_DELETE_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_delete_tag_handler)
        ],
        NEW_PLACEMARKS_PLACEMARK_NEW_TAG_APPROVE_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(new_placemarks_approve_tag_handler)
        ],
        CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(categories_and_tags_categories_handler)
        ],
        CATEGORIES_AND_TAGS_INSERT_CATEGORY_MENU_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, categories_and_tags_insert_category_handler)
        ],
        CATEGORIES_AND_TAGS_EDIT_CATEGORY_MENU_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, categories_and_tags_edit_category_handler)
        ],
        CATEGORIES_AND_TAGS_DELETE_CATEGORY_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(categories_and_tags_delete_category_handler)
        ],
        CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(categories_and_tags_tags_handler)
        ],
        CATEGORIES_AND_TAGS_INSERT_TAG_MENU_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, categories_and_tags_insert_tag_handler)
        ],
        CATEGORIES_AND_TAGS_TAG_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(categories_and_tags_tag_menu_handler)
        ],
        CATEGORIES_AND_TAGS_EDIT_TAG_HANDLER: COMMON_HANDLERS + [
            MessageHandler(filters.TEXT & TEXT_FILTER, categories_and_tags_edit_tag_handler)
        ],
        CATEGORIES_AND_TAGS_DELETE_TAG_MENU_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(categories_and_tags_delete_tag_handler)
        ],
        APPROVED_PLACEMARKS_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(approved_placemarks_selector_handler)
        ],
        APPROVED_PLACEMARKS_PLACEMARK_INFO_HANDLER: COMMON_HANDLERS + [
            CallbackQueryHandler(approved_placemarks_placemark_info_handler)
        ]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

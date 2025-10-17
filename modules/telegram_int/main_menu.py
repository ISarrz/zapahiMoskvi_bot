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


@async_logger
async def start(update: Update, context: CallbackContext):
    User.safe_insert(update.effective_user.id)
    user = User(telegram_id=int(update.effective_user.id))
    text = ("Привет! Это бот, отслеживающий запахи Москвы. "
            "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
            "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
            "готовым нотам, разбитым на категории.")

    # reply_keyboard = [
    #     ["Добавить метку", "Все метки"],
    #     ["Мои метки", "Напоминания"],
    #     ["О нас"],
    # ]
    reply_keyboard = [
        ["Добавить метку", "Все метки"],
        ["Напоминания"],
        ["О нас"],
    ]

    # if user.role == "admin":
    #     reply_keyboard.append(["Новые метки", "Категории и теги"])

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Выберите раздел"
        ),
    )

    return MAIN_MENU_HANDLER


async def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


ConversationHandler_main_menu = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        MAIN_MENU_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
        ],
        PLACEMARK_INSERTER_LOCATION_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
            MessageHandler(filters.LOCATION, insert_placemark_location_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        PLACEMARK_INSERTER_DESCRIPTION_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
            MessageHandler(filters.TEXT & ~filters.Regex(
                "(?i)^(Добавить метку|Все метки|Мои метки|Напоминания|О нас|Новые метки|Категории и теги)$"),
                           insert_placemark_description_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        PLACEMARK_INSERTER_CATEGORIES_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
            CallbackQueryHandler(insert_placemark_categories_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        PLACEMARK_INSERTER_TAGS_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
            CallbackQueryHandler(insert_placemark_tags_handler),
        ],
        PLACEMARK_INSERTER_INSERT_TAG_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),
            MessageHandler(filters.TEXT & ~filters.Regex(
                "(?i)^(Добавить метку|Все метки|Мои метки|Напоминания|О нас|Новые метки|Категории и теги)$"),
                           insert_placemark_insert_tag_handler),
            CallbackQueryHandler(insert_placemark_handler)
        ],
        WEEKDAYS_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), ),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),

            CallbackQueryHandler(weekdays_handler)
        ],
        HOURS_HANDLER: [
            MessageHandler(filters.Regex("(?i)^(Добавить метку)$"), insert_placemark_handler),
            MessageHandler(filters.Regex("(?i)^(Все метки)$"), all_placemarks_handler),
            # MessageHandler(filters.Regex("(?i)^(Мои метки)$"), scene2),
            MessageHandler(filters.Regex("(?i)^(Напоминания)$"), notifications_handler),
            MessageHandler(filters.Regex("(?i)^(О нас)$"), about_handler),
            # MessageHandler(filters.Regex("(?i)^(Новые метки)$"), scene2),
            # MessageHandler(filters.Regex("(?i)^(Категории и теги)$"), scene2),

            CallbackQueryHandler(time_handler)
        ]
    },

    fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    allow_reentry=True,
    per_message=False
)

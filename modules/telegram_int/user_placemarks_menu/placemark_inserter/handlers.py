from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag
from modules.database.user.user import User
from modules.telegram_int.user_placemarks_menu.constants import *
from modules.telegram_int.user_placemarks_menu.placemark_inserter.support_functions import get_address
from modules.telegram_int.user_placemarks_menu.placemark_inserter.support_functions import insert_user_placemark

from modules.telegram_int.user_placemarks_menu.placemark_inserter.sheets_generators import \
    placemark_inserter_get_tags_sheets

from modules.telegram_int.user_placemarks_menu.placemark_inserter.sheets_generators import \
    placemark_inserter_get_categories_sheets

from modules.telegram_int.user_placemarks_menu.placemark_inserter.messages_interactions import \
    placemark_inserter_update_tags_menu

from modules.telegram_int.user_placemarks_menu.placemark_inserter.messages_interactions import (
    placemark_inserter_update_categories_menu,
    placemark_inserter_send_categories_menu,
placemark_inserter_send_tags_menu
)


async def placemark_inserter_location_handler(update: Update, context: CallbackContext):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    context.user_data["latitude"] = latitude
    context.user_data["longitude"] = longitude
    message = context.user_data['placemark_message']
    context.user_data["address"] = get_address(latitude, longitude)
    await update.message.reply_text("Отправьте описание для адреса " + context.user_data["address"])

    return PLACEMARK_INSERTER_DESCRIPTION_HANDLER


async def placemark_inserter_description_handler(update: Update, context: CallbackContext):
    description = update.message.text
    context.user_data["description"] = description

    await placemark_inserter_send_categories_menu(update, context)

    return PLACEMARK_INSERTER_CATEGORIES_HANDLER


async def placemark_inserter_categories_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        sheets = await placemark_inserter_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] -= 1
        context.user_data['categories_sheet'] += len(sheets)
        context.user_data['categories_sheet'] %= len(sheets)

        await placemark_inserter_update_categories_menu(update, context)

        return PLACEMARK_INSERTER_CATEGORIES_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await placemark_inserter_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] += 1
        context.user_data['categories_sheet'] %= len(sheets)

        await placemark_inserter_update_categories_menu(update, context)

        return PLACEMARK_INSERTER_CATEGORIES_HANDLER

    elif income == "skip":
        await insert_user_placemark(update, context)
        context.user_data["tags"] = []

        return ConversationHandler.END


    else:
        context.user_data['category_id'] = int(income)
        await placemark_inserter_update_tags_menu(update, context)

        return PLACEMARK_INSERTER_TAGS_HANDLER


async def placemark_inserter_tags_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await placemark_inserter_update_categories_menu(update, context)

        return PLACEMARK_INSERTER_CATEGORIES_HANDLER

    elif income == LEFT_ARROW:
        sheets = await placemark_inserter_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)

        await placemark_inserter_update_tags_menu(update, context)

        return PLACEMARK_INSERTER_TAGS_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await placemark_inserter_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)

        await placemark_inserter_update_tags_menu(update, context)

        return PLACEMARK_INSERTER_TAGS_HANDLER

    elif income == "skip":
        await insert_user_placemark(update, context)
        context.user_data["tags"] = []

        return ConversationHandler.END

    elif income == ADD:
        message = context.user_data['placemark_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название тега",
            reply_markup=None
        )

        return PLACEMARK_INSERTER_INSERT_TAG_HANDLER

    else:
        if int(income) in context.user_data["tags"]:
            context.user_data["tags"].remove(int(income))

            await placemark_inserter_update_tags_menu(update, context)

        elif len(context.user_data["tags"]) < 3:
            context.user_data['tags'].append(int(income))

            await placemark_inserter_update_tags_menu(update, context)

        return PLACEMARK_INSERTER_TAGS_HANDLER


async def placemark_inserter_insert_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    tag = Tag.safe_insert(name=name, user_id=user.id)
    category = Category(id=int(context.user_data['category_id']))
    tag.insert_category(category)

    await placemark_inserter_send_tags_menu(update, context)

    return PLACEMARK_INSERTER_TAGS_HANDLER

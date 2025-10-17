
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from modules.logger.logger import logger, async_logger
from modules.database.user.user import User
from modules.database.placemark.placemark import Placemark
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag

from modules.telegram_int.user_placemarks_menu.constants import *
from modules.telegram_int.user_placemarks_menu.placemark_editor.messages_interactions import (
    placemark_editor_update_delete_menu,
    placemark_editor_send_edit_menu,
    placemark_editor_update_edit_menu,
    placemark_editor_send_placemark_info_menu,
    placemark_editor_update_placemark_info_menu,
    placemark_editor_update_categories_menu,
    placemark_editor_send_categories_menu,
    placemark_editor_update_tags_menu,
    placemark_editor_send_tags_menu,
)
from modules.telegram_int.user_placemarks_menu.placemark_editor.sheets_generators import (
    placemark_editor_get_categories_sheets,
    placemark_editor_get_tags_sheets,
)
from modules.telegram_int.user_placemarks_menu.placemark_editor.support_functions import update_placemark

from modules.telegram_int.user_placemarks_menu.placemark_selector.messages_interactions import \
    placemark_selector_update_placemarks_menu


async def placemark_editor_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await placemark_selector_update_placemarks_menu(update, context)

        return PLACEMARK_SELECTOR_HANDLER

    elif income == DELETE:
        await placemark_editor_update_delete_menu(update, context)

        return PLACEMARK_EDITOR_DELETE_HANDLER

    elif income == EDIT:
        await placemark_editor_update_edit_menu(update, context)

        return PLACEMARK_EDITOR_EDIT_MENU_HANDLER

    await placemark_editor_update_placemark_info_menu(update, context)

    return PLACEMARK_SELECTOR_HANDLER


async def placemark_editor_placemark_edit_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await placemark_editor_update_placemark_info_menu(update, context)
        return PLACEMARK_EDITOR_HANDLER

    elif income == "address":
        message = context.user_data['placemark_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите адресс",
            reply_markup=None
        )

        return PLACEMARK_EDITOR_ADDRESS_HANDLER


    elif income == "location":
        message = context.user_data['placemark_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Отравьте локацию",
            reply_markup=None
        )

        return PLACEMARK_EDITOR_LOCATION_HANDLER

    elif income == "description":
        message = context.user_data['placemark_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите описание",
            reply_markup=None
        )

        return PLACEMARK_EDITOR_DESCRIPTION_HANDLER

    elif income == "tags":
        context.user_data['tags'] = []
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        for tag in placemark.tags:
            context.user_data['tags'].append(tag.id)

        context.user_data['categories_sheet'] = 0
        await placemark_editor_update_categories_menu(update, context)

        return PLACEMARK_EDITOR_CATEGORIES_HANDLER

    # await update_edit_menu(update, context)
    # return PLACEMARKS_EDITOR_HANDLER


async def placemark_editor_placemark_edit_address_handler(update: Update, context: CallbackContext):
    address = update.message.text
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.address = address

    await placemark_editor_send_edit_menu(update, context)

    return PLACEMARK_EDITOR_EDIT_MENU_HANDLER


async def placemark_editor_placemark_edit_location_handler(update: Update, context: CallbackContext):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.latitude = latitude
    placemark.longitude = longitude

    await placemark_editor_send_edit_menu(update, context)

    return PLACEMARK_EDITOR_EDIT_MENU_HANDLER




async def placemark_editor_placemark_edit_description_handler(update: Update, context: CallbackContext):
    description = update.message.text
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.description = description

    await placemark_editor_send_edit_menu(update, context)

    return PLACEMARK_EDITOR_EDIT_MENU_HANDLER


async def placemark_editor_categories_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        sheets = await placemark_editor_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] -= 1
        context.user_data['categories_sheet'] += len(sheets)
        context.user_data['categories_sheet'] %= len(sheets)

        await placemark_editor_update_categories_menu(update, context)

        return PLACEMARK_EDITOR_CATEGORIES_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await placemark_editor_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] += 1
        context.user_data['categories_sheet'] %= len(sheets)

        await placemark_editor_update_categories_menu(update, context)

        return PLACEMARK_EDITOR_CATEGORIES_HANDLER

    elif income == "skip":
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        for tag in placemark.tags:
            placemark.delete_tag(tag)

        for tag_id in context.user_data['tags']:
            tag = Tag(id=tag_id)
            placemark.insert_tag(tag)

        await placemark_editor_update_edit_menu(update, context)

        return PLACEMARK_EDITOR_EDIT_MENU_HANDLER


    else:
        context.user_data['category_id'] = int(income)
        await placemark_editor_update_tags_menu(update, context)

        return PLACEMARK_EDITOR_TAGS_HANDLER


async def placemark_editor_tags_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await placemark_editor_update_categories_menu(update, context)

        return PLACEMARK_INSERTER_CATEGORIES_HANDLER

    elif income == LEFT_ARROW:
        sheets = await placemark_editor_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)

        await placemark_editor_update_tags_menu(update, context)

        return PLACEMARK_EDITOR_TAGS_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await placemark_editor_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)

        await placemark_editor_update_tags_menu(update, context)

        return PLACEMARK_EDITOR_TAGS_HANDLER

    elif income == "skip":
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        for tag in placemark.tags:
            placemark.delete_tag(tag)

        for tag_id in context.user_data['tags']:
            tag = Tag(id=tag_id)
            placemark.insert_tag(tag)

        await placemark_editor_update_edit_menu(update, context)

        return PLACEMARK_EDITOR_EDIT_MENU_HANDLER

    elif income == ADD:
        message = context.user_data['placemark_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="введите название тега",
            reply_markup=None
        )

        return PLACEMARK_EDITOR_INSERT_TAG_HANDLER

    else:
        if int(income) in context.user_data["tags"]:
            context.user_data["tags"].remove(int(income))

        else:
            context.user_data['tags'].append(int(income))

        await placemark_editor_update_tags_menu(update, context)

        return PLACEMARK_EDITOR_TAGS_HANDLER


async def placemark_editor_insert_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    tag = Tag.safe_insert(name=name, user_id=user.id)
    category = Category(id=int(context.user_data['category_id']))
    tag.insert_category(category)

    await placemark_editor_send_tags_menu(update, context)

    return PLACEMARK_EDITOR_TAGS_HANDLER


@async_logger
async def placemark_editor_delete_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        placemark.delete()

        await placemark_selector_update_placemarks_menu(update, context)

        return PLACEMARK_SELECTOR_HANDLER

    elif income == CANCEL:
        await placemark_editor_update_placemark_info_menu(update, context)

        return PLACEMARK_EDITOR_HANDLER

    return ConversationHandler.END

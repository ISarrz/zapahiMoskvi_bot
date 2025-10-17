from telegram import (
    Update
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from modules.telegram_int.constants import *
from modules.telegram_int.edit_placemarks.sheets_generators import (
    edit_placemarks_get_placemarks_sheets
)
from modules.telegram_int.edit_placemarks.support_functions import (
    get_address
)
from modules.logger.logger import  async_logger
from modules.database.user.user import User
from modules.database.placemark.placemark import Placemark
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag

from modules.telegram_int.edit_placemarks.messages_interactions import (
    edit_placemarks_update_delete_menu,
    edit_placemarks_send_edit_menu,
    edit_placemarks_update_edit_menu,
    edit_placemarks_update_placemark_info_menu,
    edit_placemarks_update_categories_menu,
    edit_placemarks_update_tags_menu,
    edit_placemarks_send_tags_menu,
    edit_placemarks_placemark_selector_update_placemarks_menu,
    edit_placemarks_placemark_selector_send_placemarks_menu,

)
from modules.telegram_int.edit_placemarks.sheets_generators import (
    edit_placemarks_get_categories_sheets,
    edit_placemarks_get_tags_sheets,
)


@async_logger
async def edit_placemarks_handler(update: Update, context: CallbackContext):
    context.user_data['placemark_sheet'] = 0
    await edit_placemarks_placemark_selector_send_placemarks_menu(update, context)

    return EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER


@async_logger
async def edit_placemarks_placemarks_selector_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data['placemark_sheet'] -= 1
        sheets = edit_placemarks_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
        context.user_data['placemark_sheet'] += len(sheets)
        context.user_data['placemark_sheet'] %= len(sheets)

        await edit_placemarks_placemark_selector_update_placemarks_menu(update, context)

        return EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data['placemark_sheet'] += 1
        sheets = edit_placemarks_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
        context.user_data['placemark_sheet'] %= len(sheets)

        await edit_placemarks_placemark_selector_update_placemarks_menu(update, context)

        return EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER

    else:
        context.user_data['selected_placemark_id'] = int(income)
        await edit_placemarks_update_placemark_info_menu(update, context)
        return EDIT_PLACEMARKS_HANDLER


@async_logger
async def edit_placemarks_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await edit_placemarks_placemark_selector_update_placemarks_menu(update, context)

        return EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER

    elif income == DELETE:
        await edit_placemarks_update_delete_menu(update, context)

        return EDIT_PLACEMARKS_DELETE_HANDLER

    elif income == EDIT:
        await edit_placemarks_update_edit_menu(update, context)

        return EDIT_PLACEMARKS_EDIT_MENU_HANDLER

    await edit_placemarks_update_placemark_info_menu(update, context)

    return EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER


@async_logger
async def edit_placemarks_placemark_edit_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await edit_placemarks_update_placemark_info_menu(update, context)
        return EDIT_PLACEMARKS_HANDLER

    elif income == "address":
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите адресс",
            reply_markup=None
        )

        return EDIT_PLACEMARKS_ADDRESS_HANDLER


    elif income == "location":
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Отравьте локацию",
            reply_markup=None
        )

        return EDIT_PLACEMARKS_LOCATION_HANDLER

    elif income == "description":
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите описание",
            reply_markup=None
        )

        return EDIT_PLACEMARKS_DESCRIPTION_HANDLER

    elif income == "tags":
        context.user_data['tags'] = []
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        for tag in placemark.tags:
            context.user_data['tags'].append(tag.id)

        context.user_data['categories_sheet'] = 0
        await edit_placemarks_update_categories_menu(update, context)

        return EDIT_PLACEMARKS_CATEGORIES_HANDLER

    return ConversationHandler.END

@async_logger
async def edit_placemarks_placemark_edit_address_handler(update: Update, context: CallbackContext):
    address = update.message.text
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.address = address

    await edit_placemarks_send_edit_menu(update, context)

    return EDIT_PLACEMARKS_EDIT_MENU_HANDLER


@async_logger
async def edit_placemarks_placemark_edit_location_handler(update: Update, context: CallbackContext):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.latitude = latitude
    placemark.longitude = longitude
    placemark.address = get_address(latitude, longitude)

    await edit_placemarks_send_edit_menu(update, context)

    return EDIT_PLACEMARKS_EDIT_MENU_HANDLER


@async_logger
async def edit_placemarks_placemark_edit_description_handler(update: Update, context: CallbackContext):
    description = update.message.text
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.description = description

    await edit_placemarks_send_edit_menu(update, context)

    return EDIT_PLACEMARKS_EDIT_MENU_HANDLER


@async_logger
async def edit_placemarks_categories_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        sheets = await edit_placemarks_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] -= 1
        context.user_data['categories_sheet'] += len(sheets)
        context.user_data['categories_sheet'] %= len(sheets)

        await edit_placemarks_update_categories_menu(update, context)

        return EDIT_PLACEMARKS_CATEGORIES_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await edit_placemarks_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] += 1
        context.user_data['categories_sheet'] %= len(sheets)

        await edit_placemarks_update_categories_menu(update, context)

        return EDIT_PLACEMARKS_CATEGORIES_HANDLER

    elif income == "skip":
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        for tag in placemark.tags:
            placemark.delete_tag(tag)

        for tag_id in context.user_data['tags']:
            tag = Tag(id=tag_id)
            placemark.insert_tag(tag)

        await edit_placemarks_update_edit_menu(update, context)

        return EDIT_PLACEMARKS_EDIT_MENU_HANDLER


    else:
        context.user_data['category_id'] = int(income)
        await edit_placemarks_update_tags_menu(update, context)

        return EDIT_PLACEMARKS_TAGS_HANDLER


@async_logger
async def edit_placemarks_tags_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await edit_placemarks_update_categories_menu(update, context)

        return PLACEMARK_INSERTER_CATEGORIES_HANDLER

    elif income == LEFT_ARROW:
        sheets = await edit_placemarks_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)

        await edit_placemarks_update_tags_menu(update, context)

        return EDIT_PLACEMARKS_TAGS_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await edit_placemarks_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)

        await edit_placemarks_update_tags_menu(update, context)

        return EDIT_PLACEMARKS_TAGS_HANDLER

    elif income == "skip":
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        for tag in placemark.tags:
            placemark.delete_tag(tag)

        for tag_id in context.user_data['tags']:
            tag = Tag(id=tag_id)
            placemark.insert_tag(tag)

        await edit_placemarks_update_edit_menu(update, context)

        return EDIT_PLACEMARKS_EDIT_MENU_HANDLER

    elif income == ADD:
        message = context.user_data['message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="введите название тега",
            reply_markup=None
        )

        return EDIT_PLACEMARKS_INSERT_TAG_HANDLER

    else:
        if int(income) in context.user_data["tags"]:
            context.user_data["tags"].remove(int(income))

        else:
            context.user_data['tags'].append(int(income))

        await edit_placemarks_update_tags_menu(update, context)

        return EDIT_PLACEMARKS_TAGS_HANDLER


@async_logger
async def edit_placemarks_insert_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    tag = Tag.safe_insert(name=name, user_id=user.id)
    category = Category(id=int(context.user_data['category_id']))
    tag.insert_category(category)

    await edit_placemarks_send_tags_menu(update, context)

    return EDIT_PLACEMARKS_TAGS_HANDLER


@async_logger
async def edit_placemarks_delete_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        placemark.delete()

        await edit_placemarks_placemark_selector_update_placemarks_menu(update, context)

        return EDIT_PLACEMARKS_PLACEMARK_SELECTOR_HANDLER

    elif income == CANCEL:
        await edit_placemarks_update_placemark_info_menu(update, context)

        return EDIT_PLACEMARKS_HANDLER

    return ConversationHandler.END

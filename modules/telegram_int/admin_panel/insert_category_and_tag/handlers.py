from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from modules.logger.logger import async_logger
from modules.telegram_int.admin_panel.constants import *
from modules.telegram_int.admin_panel.approved_placemarks.messages_interactions import (
    approved_placemarks_update_placemarks_menu
)
from modules.telegram_int.admin_panel.mode_selector.messages_interactions import (
    mode_selector_update_menu
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.telegram_int.admin_panel.insert_category_and_tag.sheets_generators import (
    insert_category_and_tag_get_categories_sheets,
    insert_category_and_tag_get_tags_sheets
)
from modules.telegram_int.admin_panel.insert_category_and_tag.messages_interactions import (
    insert_category_and_tag_update_categories_menu,
    insert_category_and_tag_update_tags_menu,
    insert_category_and_tag_send_categories_menu,
    insert_category_and_tag_send_tags_menu
)
from modules.database.user.user import User
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag


async def insert_category_and_tag_categories_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await mode_selector_update_menu(update, context)

        return MODE_SELECTOR_HANDLER

    elif income == LEFT_ARROW:
        sheets = await insert_category_and_tag_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] -= 1
        context.user_data['categories_sheet'] += len(sheets)
        context.user_data['categories_sheet'] %= len(sheets)

        await insert_category_and_tag_update_categories_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await insert_category_and_tag_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] += 1
        context.user_data['categories_sheet'] %= len(sheets)

        await insert_category_and_tag_update_categories_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER

    elif income == ADD:
        message = context.user_data['admin_panel_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название категории",
            reply_markup=None
        )

        return INSERT_CATEGORY_AND_TAG_INSERT_CATEGORY_MENU_HANDLER

    else:
        context.user_data['category_id'] = int(income)
        await insert_category_and_tag_update_tags_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER


async def insert_category_and_tag_insert_category_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    Category.safe_insert(name=name, user_id=user.id, status="approved")

    await insert_category_and_tag_send_categories_menu(update, context)

    return INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER


async def insert_category_and_tag_edit_category_handler(update: Update, context: CallbackContext):
    name = update.message.text
    category = Category(id=int(context.user_data['category_id']))
    category.name = name

    await insert_category_and_tag_send_tags_menu(update, context)

    return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER


async def insert_category_and_tag_delete_category_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        category = Category(id=int(context.user_data['category_id']))
        category.delete()

    await insert_category_and_tag_update_categories_menu(update, context)

    return INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER


async def insert_category_and_tag_tags_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await insert_category_and_tag_update_categories_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_CATEGORIES_MENU_HANDLER

    elif income == LEFT_ARROW:
        sheets = await insert_category_and_tag_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)

        await insert_category_and_tag_update_tags_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await insert_category_and_tag_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)

        await insert_category_and_tag_update_tags_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER


    elif income == DELETE:
        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]

        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['admin_panel_message']
        category = Category(id=int(context.user_data['category_id']))

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Удалить категорию " + category.name + "?",
            reply_markup=reply_markup
        )

        return INSERT_CATEGORY_AND_TAG_DELETE_CATEGORY_MENU_HANDLER

    elif income == EDIT:
        message = context.user_data['admin_panel_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите новое название категории",
            reply_markup=None
        )

        return INSERT_CATEGORY_AND_TAG_EDIT_CATEGORY_MENU_HANDLER

    elif income == ADD:
        message = context.user_data['admin_panel_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название тега",
            reply_markup=None
        )

        return INSERT_CATEGORY_AND_TAG_INSERT_TAG_MENU_HANDLER

    else:
        context.user_data['tag_id'] = int(income)
        sheet = [[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=EDIT, callback_data=EDIT),
            InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]]

        tag = Tag(id=int(context.user_data['tag_id']))
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['admin_panel_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Тег " + tag.name,
            reply_markup=reply_markup
        )

        return INSERT_CATEGORY_AND_TAG_TAG_MENU_HANDLER


async def insert_category_and_tag_insert_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    tag = Tag.safe_insert(name=name, user_id=user.id,status="approved")
    category = Category(id=int(context.user_data['category_id']))
    tag.insert_category(category)

    await insert_category_and_tag_send_tags_menu(update, context)

    return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER


async def insert_category_and_tag_tag_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await insert_category_and_tag_update_tags_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER

    elif income == EDIT:
        message = context.user_data['admin_panel_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название тега",
            reply_markup=None
        )

        return INSERT_CATEGORY_AND_TAG_EDIT_TAG_HANDLER

    elif income == DELETE:
        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]

        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['admin_panel_message']
        tag = Tag(id=int(context.user_data['tag_id']))

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Удалить тег " + tag.name + "?",
            reply_markup=reply_markup
        )

        return INSERT_CATEGORY_AND_TAG_DELETE_TAG_MENU_HANDLER


async def insert_category_and_tag_edit_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text
    tag = Tag(id=int(context.user_data['tag_id']))
    tag.name = name

    sheet = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ]]

    tag = Tag(id=int(context.user_data['tag_id']))
    reply_markup = InlineKeyboardMarkup(sheet)


    message =     await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Тег " + tag.name,
        reply_markup=reply_markup
    )
    context.user_data['admin_panel_message'] = message
    return INSERT_CATEGORY_AND_TAG_TAG_MENU_HANDLER


async def insert_category_and_tag_delete_tag_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))
        tag.delete()
        await insert_category_and_tag_update_tags_menu(update, context)

        return INSERT_CATEGORY_AND_TAG_TAGS_MENU_HANDLER
    else:
        sheet = [[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=EDIT, callback_data=EDIT),
            InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]]

        tag = Tag(id=int(context.user_data['tag_id']))
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['admin_panel_message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Тег " + tag.name,
            reply_markup=reply_markup
        )

        return INSERT_CATEGORY_AND_TAG_TAG_MENU_HANDLER


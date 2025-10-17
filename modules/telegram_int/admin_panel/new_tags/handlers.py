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

from modules.database.user.user import User
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag
from modules.telegram_int.admin_panel.new_tags.messages_interactions import (
    new_tags_send_tags_menu,
    new_tags_update_tags_menu,
    new_tags_update_tag_menu,
    new_tags_send_tag_menu
)
from modules.telegram_int.admin_panel.mode_selector.messages_interactions import (
    mode_selector_update_menu
)
from modules.telegram_int.admin_panel.new_tags.sheets_generators import new_tags_get_tags_sheets


async def new_tags_tags_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await mode_selector_update_menu(update, context)

        return MODE_SELECTOR_HANDLER

    elif income == LEFT_ARROW:
        sheets = await new_tags_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)
        await new_tags_update_tags_menu(update, context)

        return NEW_TAGS_TAGS_MENU_HANDLER
    elif income == RIGHT_ARROW:
        sheets = await new_tags_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)
        await new_tags_update_tags_menu(update, context)

        return NEW_TAGS_TAGS_MENU_HANDLER

    else:

        context.user_data['tag_id'] = int(income)
        await new_tags_update_tag_menu(update, context)

        return NEW_TAGS_TAG_MENU_HANDLER


async def new_tags_tag_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == EDIT:
        tag = Tag(id=int(context.user_data['tag_id']))

        message = context.user_data['admin_panel_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите новое название для тега " + tag.name,
            reply_markup=None
        )

        return NEW_TAGS_TAG_EDIT_HANDLER

    elif income == BACK_ARROW:
        await new_tags_update_tags_menu(update, context)

        return NEW_TAGS_TAGS_MENU_HANDLER

    elif income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))

        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['admin_panel_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Добавить тег " + tag.name + "?",
            reply_markup=reply_markup
        )

        return NEW_TAGS_TAG_APPROVE_HANDLER

    elif income == DELETE:
        tag = Tag(id=int(context.user_data['tag_id']))

        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['admin_panel_message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Удалить тег " + tag.name + "?",
            reply_markup=reply_markup
        )

        return NEW_TAGS_TAG_DELETE_HANDLER


async def new_tags_tag_edit_handler(update: Update, context: CallbackContext):
    name = update.message.text
    tag = Tag(id=int(context.user_data['tag_id']))
    tag.name = name

    await new_tags_send_tag_menu(update, context)

    return NEW_TAGS_TAG_MENU_HANDLER


async def new_tags_delete_tag_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))
        tag.delete()
        await new_tags_update_tags_menu(update, context)
        return NEW_TAGS_TAGS_MENU_HANDLER

    else:
        await new_tags_update_tag_menu(update, context)
        return NEW_TAGS_TAG_MENU_HANDLER


async def new_tags_approve_tag_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))
        tag.approve()
        await new_tags_update_tags_menu(update, context)
        return NEW_TAGS_TAGS_MENU_HANDLER

    else:
        await new_tags_update_tag_menu(update, context)
        return NEW_TAGS_TAG_MENU_HANDLER

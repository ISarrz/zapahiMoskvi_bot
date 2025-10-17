from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag
from modules.telegram_int.admin_panel.new_tags.sheets_generators import new_tags_get_tags_sheets
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.telegram_int.admin_panel.constants import *


async def new_tags_update_tags_menu(update: Update, context: CallbackContext):
    sheets = await new_tags_get_tags_sheets(update, context)
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег"

    message = context.user_data['admin_panel_message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def new_tags_send_tags_menu(update: Update, context: CallbackContext):
    sheets = await new_tags_get_tags_sheets(update, context)
    context.user_data['tags_sheet'] = 0
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['admin_panel_message'] = message


async def new_tags_send_tag_menu(update: Update, context: CallbackContext):
    tag = Tag(id=int(context.user_data['tag_id']))
    category_id = tag.category_id
    if category_id != -1:
        category = Category(id=category_id)
        text = "Тег " + tag.name + "из категории " + category.name
    else:
        text = "Тег " + tag.name

    sheet = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ]]
    reply_markup = InlineKeyboardMarkup(sheet)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    context.user_data['admin_panel_message'] = message


async def new_tags_update_tag_menu(update: Update, context: CallbackContext):
    tag = Tag(id=int(context.user_data['tag_id']))
    category_id = tag.category_id
    if category_id != -1:
        category = Category(id=category_id)
        text = "Тег " + tag.name + "из категории " + category.name
    else:
        text = "Тег " + tag.name

    sheet = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ]]
    reply_markup = InlineKeyboardMarkup(sheet)
    message = context.user_data['admin_panel_message']
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

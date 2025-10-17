from telegram import InlineKeyboardButton
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext
from modules.telegram_int.admin_panel.constants import *
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag
from modules.database.user.user import User


async def new_tags_get_tags_sheets(update: Update, context: CallbackContext):
    tags = Tag.pending()

    sheets = []
    for tag in tags:
        if not sheets or len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH:
            sheets.append([])
        text  = tag.name

        sheets[-1].append([InlineKeyboardButton(text=text, callback_data=tag.id)])

    for i in range(len(sheets)):
        if len(sheets) > 1:
            sheets[i].append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
            ])
        else:
            sheets[i].append([
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        ]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets
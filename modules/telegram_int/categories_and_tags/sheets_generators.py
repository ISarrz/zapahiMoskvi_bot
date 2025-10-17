from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext
from modules.telegram_int.constants import *
from modules.database.placemark.category import Category

async def categories_and_tags_get_categories_sheets(update: Update, context: CallbackContext):
    categories = Category.approved()
    sheets = []
    for category in categories:
        if not sheets or len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH:
            sheets.append([])

        sheets[-1].append([InlineKeyboardButton(text=category.name, callback_data=category.id)])

    for i in range(len(sheets)):
        if len(sheets) > 1:
            sheets[i].append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text = ADD, callback_data=ADD),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
            ])
        else:
            sheets[i].append([
                InlineKeyboardButton(text=ADD, callback_data=ADD),
            ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[
            InlineKeyboardButton(text=ADD, callback_data=ADD),
        ]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets


async def categories_and_tags_get_tags_sheets(update: Update, context: CallbackContext):
    category = Category(id=int(context.user_data['category_id']))

    tags = []
    for tag in category.tags:
        if tag.status == "approved" :
            tags.append(tag)

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
                InlineKeyboardButton(text=ADD, callback_data=ADD),
                InlineKeyboardButton(text=EDIT, callback_data=EDIT),
                InlineKeyboardButton(text=DELETE, callback_data=DELETE),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
            ])
        else:
            sheets[i].append([
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text=ADD, callback_data=ADD),
                InlineKeyboardButton(text=EDIT, callback_data=EDIT),
                InlineKeyboardButton(text=DELETE, callback_data=DELETE),
            ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=ADD, callback_data=ADD),
                InlineKeyboardButton(text=EDIT, callback_data=EDIT),
                InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets

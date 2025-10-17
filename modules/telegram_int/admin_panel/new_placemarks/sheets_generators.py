from telegram import InlineKeyboardButton
from modules.database.user.user import User
from modules.database.placemark.placemark import Placemark
from modules.telegram_int.admin_panel.constants import *
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,

)
from telegram.ext import CallbackContext
from modules.database.placemark.tag import Tag


def new_placemarks_get_placemarks_sheets():
    placemarks = Placemark.get_pending()

    sheets = []

    for placemark in placemarks:
        if not sheets or len(sheets[-1]) >= MAX_SHEET_LENGTH:
            sheets.append([])

        sheets[-1].append([InlineKeyboardButton(text=placemark.address, callback_data=placemark.id)])

    for i in range(len(sheets)):
        sheet = sheets[i]
        if len(sheets) > 1:
            sheet.append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])
        else:
            sheet.append([InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)])

    return sheets


async def new_placemarks_get_placemark_new_tags_sheets(update: Update, context: CallbackContext):
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    tags = [tag for tag in placemark.tags if tag.status == "pending"]

    sheets = []
    for tag in tags:
        if not sheets or len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH:
            sheets.append([])
        text = tag.name

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

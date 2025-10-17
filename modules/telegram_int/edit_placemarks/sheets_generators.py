from modules.database.placemark.placemark import Placemark
from modules.telegram_int.constants import *
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


from telegram.ext import CallbackContext
from modules.database.user.user import User
from modules.database.placemark.category import Category



def edit_placemarks_get_placemarks_sheets(user: User):
    sheets = []
    if not user.placemarks:
        return [None]

    placemarks = [Placemark(id=placemark.id) for placemark in user.placemarks]
    cur_sheet = []

    for placemark in placemarks:
        if len(cur_sheet) >= MAX_SHEET_LENGTH:
            sheets.append(cur_sheet)
            cur_sheet = []

        cur_sheet.append([InlineKeyboardButton(text=placemark.address, callback_data=placemark.id)])

    if cur_sheet:
        sheets.append(cur_sheet)

    for i in range(len(sheets)):
        sheet = sheets[i]
        if len(sheets) > 1:
            sheet.append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])


    return sheets


async def edit_placemarks_get_categories_sheets(update: Update, context: CallbackContext):
    user = User(telegram_id=int(update.effective_user.id))
    categories = Category.approved_and_user(user.id)
    sheets = []
    for category in categories:
        if not sheets or len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH:
            sheets.append([])

        sheets[-1].append([InlineKeyboardButton(text=category.name, callback_data=category.id)])

    for i in range(len(sheets)):
        if len(sheets) > 1:
            sheets[i].append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text="Пропустить" if not context.user_data["tags"] else "Подтвердить", callback_data="skip"),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
            ])
        else:
            sheets[i].append([
                InlineKeyboardButton(text="Пропустить" if not context.user_data["tags"] else "Подтвердить", callback_data="skip"),
            ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[
            InlineKeyboardButton(text="Пропустить" if not context.user_data["tags"] else "Подтвердить", callback_data="skip"),

        ]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets


async def edit_placemarks_get_tags_sheets(update: Update, context: CallbackContext):
    category = Category(id=int(context.user_data['category_id']))

    tags = []
    user = User(telegram_id=int(update.effective_user.id))
    for tag in category.tags:
        if tag.status == "approved" or tag.user_id == user.id:
            tags.append(tag)

    sheets = []
    for tag in tags:
        if not sheets or len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH:
            sheets.append([])
        text  = tag.name
        if tag.id in context.user_data["tags"]:
            text += " " + SUBMIT

        sheets[-1].append([InlineKeyboardButton(text=text, callback_data=tag.id)])

    for i in range(len(sheets)):
        if len(sheets) > 1:
            sheets[i].append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text=ADD, callback_data=ADD),
                InlineKeyboardButton(text="Пропустить" if not context.user_data["tags"] else "Подтвердить", callback_data="skip"),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
            ])
        else:
            sheets[i].append([
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text=ADD, callback_data=ADD),
                InlineKeyboardButton(text="Пропустить" if not context.user_data["tags"] else "Подтвердить", callback_data="skip"),
            ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=ADD, callback_data=ADD),
            InlineKeyboardButton(text="Пропустить" if not context.user_data["tags"] else "Подтвердить", callback_data="skip"),
        ]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets

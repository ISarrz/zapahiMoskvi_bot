from telegram import InlineKeyboardButton
from modules.database.user.user import User
from modules.database.placemark.placemark import Placemark
from modules.telegram_int.user_placemarks_menu.constants import *


def placemark_selector_get_placemarks_sheets(user: User):
    sheets = []
    if not user.placemarks:
        return [[[InlineKeyboardButton(text=ADD, callback_data=ADD)]]]

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
                InlineKeyboardButton(text=ADD, callback_data=ADD),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])
        else:
            sheet.append([
                InlineKeyboardButton(text=ADD, callback_data=ADD)
            ])

    return sheets

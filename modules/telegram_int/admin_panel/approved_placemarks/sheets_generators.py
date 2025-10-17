from telegram import InlineKeyboardButton
from modules.database.user.user import User
from modules.database.placemark.placemark import Placemark
from modules.telegram_int.admin_panel.constants import *


def approved_placemarks_get_placemarks_sheets():

    placemarks = Placemark.approved()

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

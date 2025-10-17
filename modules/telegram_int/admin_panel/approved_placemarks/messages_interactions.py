from telegram.ext import CallbackContext
from modules.telegram_int.admin_panel.approved_placemarks.sheets_generators import \
    approved_placemarks_get_placemarks_sheets
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.database.placemark.placemark import Placemark
from modules.telegram_int.admin_panel.constants import *

async def approved_placemarks_send_placemarks_menu(update: Update, context: CallbackContext):
    sheets = approved_placemarks_get_placemarks_sheets()

    sheet = sheets[context.user_data['approved_placemarks_sheet']]
    if not sheet:
        reply_markup = None
        text = "Отзывов нет"

    else:
        reply_markup = InlineKeyboardMarkup(sheet)
        text = "Принятые отзывы"

    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=text,
                                             reply_markup=reply_markup)

    context.user_data['admin_panel_message'] = message


async def approved_placemarks_update_placemarks_menu(update: Update, context: CallbackContext):
    sheets = approved_placemarks_get_placemarks_sheets()


    if not sheets:
        reply_markup =  InlineKeyboardMarkup([
            [InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)],
        ])

        text = "Отзывов нет"

    else:
        sheet = sheets[context.user_data['approved_placemarks_sheet']]
        reply_markup = InlineKeyboardMarkup(sheet)
        text = "Принятые отзывы"

    message = context.user_data['admin_panel_message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def approved_placemarks_update_placemark_info(update: Update, context: CallbackContext):
    message = context.user_data['admin_panel_message']
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    text = ""
    text += "Адресс: " + str(placemark.address) + "\n"
    text += "Дата и время создания: " + str(placemark.datetime) + "\n"
    text += "Широта: " + str(placemark.latitude) + "\n"
    text += "Долгота: " + str(placemark.longitude) + "\n"
    text += "Описание: " + str(placemark.description) + "\n"
    text += "Теги: " + ", ".join(tag.name for tag in placemark.tags) + "\n"

    keyboard = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)
    ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

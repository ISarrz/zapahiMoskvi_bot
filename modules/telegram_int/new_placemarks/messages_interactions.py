from telegram.ext import CallbackContext
from modules.telegram_int.new_placemarks.sheets_generators import (
    new_placemarks_get_placemarks_sheets,
    new_placemarks_get_placemark_new_tags_sheets
)

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.database.placemark.placemark import Placemark
from modules.database.placemark.tag import Tag
from modules.database.placemark.category import Category
from modules.telegram_int.constants import *


async def new_placemarks_send_placemarks_menu(update: Update, context: CallbackContext):
    sheets = new_placemarks_get_placemarks_sheets()

    sheet = sheets[context.user_data['new_placemarks_sheet']]
    if not sheet:
        reply_markup = None
        text = "Отзывов нет"

    else:
        reply_markup = InlineKeyboardMarkup(sheet)
        text = "Новые отзывы"

    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=text,
                                             reply_markup=reply_markup)

    context.user_data['message'] = message


async def new_placemarks_update_placemarks_menu(update: Update, context: CallbackContext):
    sheets = new_placemarks_get_placemarks_sheets()

    if not sheets or not sheets[context.user_data['new_placemarks_sheet']]:
        reply_markup = None

        text = "Отзывов нет"

    else:
        sheet = sheets[context.user_data['new_placemarks_sheet']]
        reply_markup = InlineKeyboardMarkup(sheet)
        text = "Новые отзывы"

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def new_placemarks_update_placemark_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    text = ""
    text += "Адресс: " + str(placemark.address) + "\n"
    text += "Дата и время создания: " + str(placemark.datetime) + "\n"
    text += "Широта: " + str(placemark.latitude) + "\n"
    text += "Долгота: " + str(placemark.longitude) + "\n"
    text += "Описание: " + str(placemark.description) + "\n"
    text += "Теги: " + ", ".join(tag.name for tag in placemark.tags) + "\n"

    keyboard = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
    ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def new_placemarks_update_placemark_edit_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    text = ""
    text += "Адресс: " + str(placemark.address) + "\n"
    text += "Дата и время создания: " + str(placemark.datetime) + "\n"
    text += "Широта: " + str(placemark.latitude) + "\n"
    text += "Долгота: " + str(placemark.longitude) + "\n"
    text += "Описание: " + str(placemark.description) + "\n"
    text += "Теги: " + ", ".join(tag.name for tag in placemark.tags) + "\n"

    keyboard = [
        [
            InlineKeyboardButton(text="Адресс", callback_data="address"),
            InlineKeyboardButton(text="Геометка", callback_data="geotag"),
            InlineKeyboardButton(text="Описание", callback_data="description"),
            InlineKeyboardButton(text="Теги", callback_data="tags"),
        ],
        [
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def new_placemarks_send_placemark_edit_menu(update: Update, context: CallbackContext):
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    text = ""
    text += "Адресс: " + str(placemark.address) + "\n"
    text += "Дата и время создания: " + str(placemark.datetime) + "\n"
    text += "Широта: " + str(placemark.latitude) + "\n"
    text += "Долгота: " + str(placemark.longitude) + "\n"
    text += "Описание: " + str(placemark.description) + "\n"
    text += "Теги: " + ", ".join(tag.name for tag in placemark.tags) + "\n"

    keyboard = [
        [
            InlineKeyboardButton(text="Адресс", callback_data="address"),
            InlineKeyboardButton(text="Геометка", callback_data="geotag"),
            InlineKeyboardButton(text="Описание", callback_data="description"),
            InlineKeyboardButton(text="Теги", callback_data="tags"),
        ],
        [
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    context.user_data['message'] = message


async def new_placemarks_send_tags_menu(update: Update, context: CallbackContext):
    sheets = await new_placemarks_get_placemark_new_tags_sheets(update, context)
    context.user_data['tags_sheet'] = 0
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message


async def new_placemarks_update_tags_menu(update: Update, context: CallbackContext):
    sheets = await new_placemarks_get_placemark_new_tags_sheets(update, context)
    context.user_data['tags_sheet'] = 0
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег"

    message = context.user_data['message']
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def new_placemarks_send_tag_menu(update: Update, context: CallbackContext):
    tag = Tag(id=int(context.user_data['tag_id']))
    category_id = tag.category_id
    if category_id != -1:
        category = Category(id=category_id)
        text = "Тег " + tag.name + " из категории " + category.name
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
    context.user_data['message'] = message


async def new_placemarks_update_tag_menu(update: Update, context: CallbackContext):
    tag = Tag(id=int(context.user_data['tag_id']))
    category_id = tag.category_id
    if category_id != -1:
        category = Category(id=category_id)
        text = "Тег " + tag.name + " из категории " + category.name
    else:
        text = "Тег " + tag.name

    sheet = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ]]
    reply_markup = InlineKeyboardMarkup(sheet)
    message = context.user_data['message']
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )

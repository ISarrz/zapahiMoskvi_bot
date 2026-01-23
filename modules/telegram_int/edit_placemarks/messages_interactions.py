from modules.database.user.user import User
from modules.telegram_int.edit_placemarks.sheets_generators import (
    edit_placemarks_get_placemarks_sheets
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext
from modules.database.placemark.placemark import Placemark
from modules.telegram_int.constants import *
from modules.telegram_int.edit_placemarks.sheets_generators import (
    edit_placemarks_get_categories_sheets,
    edit_placemarks_get_tags_sheets
)


async def edit_placemarks_placemark_selector_send_placemarks_menu(update: Update, context: CallbackContext):
    sheets = edit_placemarks_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
    sheet = sheets[context.user_data['placemark_sheet']]
    if sheet:
        reply_markup = InlineKeyboardMarkup(sheet)
    else:
        reply_markup = None

    if sheets and len(sheets) > 1:
        text = f"📍 Мои метки № {context.user_data['placemark_sheet'] + 1}:\n"
        text +=  " (нажмите на кнопку, чтобы увидеть метку с запахом целиком)"


    elif not sheet:
        text = "Меток нет"

    else:

        text = f"📍 Мои метки:\n"
        text += " (нажмите на кнопку, чтобы увидеть метку с запахом целиком)"

    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=text,
                                             reply_markup=reply_markup)

    context.user_data['message'] = message


async def edit_placemarks_placemark_selector_update_placemarks_menu(update: Update, context: CallbackContext):
    sheets = edit_placemarks_get_placemarks_sheets(User(telegram_id=update.effective_user.id))
    sheet = sheets[context.user_data['placemark_sheet']]
    if sheet:
        reply_markup = InlineKeyboardMarkup(sheet)
    else:
        reply_markup = None

    if len(sheets) > 1:
        text = f"📍 Мои метки № {context.user_data['placemark_sheet'] + 1}:\n"
        text += " (нажмите на кнопку, чтобы увидеть метку с запахом целиком)"
    else:
        text = f"📍 Мои метки:\n"
        text += " (нажмите на кнопку, чтобы увидеть метку с запахом целиком)"

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def edit_placemarks_update_placemark_info_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    text = ""
    text += str(placemark.address) + "\n\n"
    text += str(placemark.datetime) + "\n\n"
    text += "Описание: " + str(placemark.description) + "\n"
    text += "Теги: " + ", ".join(tag.name for tag in placemark.tags) + "\n"

    keyboard = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
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


async def edit_placemarks_send_placemark_info_menu(update: Update, context: CallbackContext):
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
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
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


async def edit_placemarks_update_delete_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']
    text = "Удалить метку?"
    keyboard = [
        [
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL)],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def edit_placemarks_update_edit_menu(update: Update, context: CallbackContext):
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
            InlineKeyboardButton(text="Локация", callback_data="location"),
        ],
        [
            InlineKeyboardButton(text="Описание", callback_data="description"),
            InlineKeyboardButton(text="Теги", callback_data="tags")
        ],
        [
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=reply_markup
    )


async def edit_placemarks_send_edit_menu(update: Update, context: CallbackContext):
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
            InlineKeyboardButton(text="Локация", callback_data="location"),
        ],
        [
            InlineKeyboardButton(text="Описание", callback_data="description"),
            InlineKeyboardButton(text="Теги", callback_data="tags")
        ],
        [
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW)
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['message'] = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )


async def edit_placemarks_send_categories_menu(update: Update, context: CallbackContext):
    context.user_data['tags_sheet'] = 0
    context.user_data['categories_sheet'] = 0
    sheets = await edit_placemarks_get_categories_sheets(update, context)
    sheet = sheets[0]

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите категорию, добавление тега можно пропустить",
        reply_markup=sheet
    )

    context.user_data['message'] = message


async def edit_placemarks_update_categories_menu(update: Update, context: CallbackContext):
    sheets = await edit_placemarks_get_categories_sheets(update, context)
    sheet = sheets[int(context.user_data['categories_sheet'])]
    context.user_data['tags_sheet'] = 0

    text = "Выберите категорию тега, добавление тега можно пропустить"

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def edit_placemarks_update_tags_menu(update: Update, context: CallbackContext):
    sheets = await edit_placemarks_get_tags_sheets(update, context)
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег или создайте свой, добавление тега можно пропустить"

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def edit_placemarks_send_tags_menu(update: Update, context: CallbackContext):
    sheets = await edit_placemarks_get_tags_sheets(update, context)
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег или создайте свой, добавление тега можно пропустить"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message

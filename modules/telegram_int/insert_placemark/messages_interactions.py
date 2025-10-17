from telegram import Update
from telegram.ext import CallbackContext

from modules.telegram_int.insert_placemark.sheets_generators import placemark_inserter_get_categories_sheets
from modules.telegram_int.insert_placemark.sheets_generators import placemark_inserter_get_tags_sheets


async def placemark_inserter_update_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Отправье геопозицию",
        reply_markup=None
    )


async def placemark_inserter_send_menu(update: Update, context: CallbackContext):
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Отправье геопозицию",
        reply_markup=None
    )

    context.user_data['message'] = message


async def placemark_inserter_send_categories_menu(update: Update, context: CallbackContext):
    context.user_data['tags_sheet'] = 0
    context.user_data['categories_sheet'] = 0
    sheets = await placemark_inserter_get_categories_sheets(update, context)
    sheet = sheets[0]

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите категорию тега, добавление тега можно пропустить",
        reply_markup=sheet
    )

    context.user_data['message'] = message


async def placemark_inserter_update_categories_menu(update: Update, context: CallbackContext):
    sheets = await placemark_inserter_get_categories_sheets(update, context)
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


async def placemark_inserter_update_tags_menu(update: Update, context: CallbackContext):
    sheets = await placemark_inserter_get_tags_sheets(update, context)
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег, но не более трех или создайте свой, добавление тега можно пропустить"

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def placemark_inserter_send_tags_menu(update: Update, context: CallbackContext):
    sheets = await placemark_inserter_get_tags_sheets(update, context)
    sheet = sheets[int(context.user_data['tags_sheet'])]

    text = "Выберите тег, но не более трех или создайте свой, добавление тега можно пропустить"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message

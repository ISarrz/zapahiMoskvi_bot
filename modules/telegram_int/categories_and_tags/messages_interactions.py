from telegram import Update
from telegram.ext import CallbackContext
from modules.telegram_int.categories_and_tags.sheets_generators import (
    categories_and_tags_get_tags_sheets,
    categories_and_tags_get_categories_sheets
)

from modules.database.placemark.category import Category


async def categories_and_tags_send_categories_menu(update: Update, context: CallbackContext):
    sheets = await categories_and_tags_get_categories_sheets(update, context)
    context.user_data['tags_sheet'] = 0
    context.user_data['categories_sheet'] = 0
    sheet = sheets[int(context.user_data['categories_sheet'])]


    text = "Выберите категорию"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message


async def categories_and_tags_update_categories_menu(update: Update, context: CallbackContext):
    sheets = await categories_and_tags_get_categories_sheets(update, context)
    sheet = sheets[int(context.user_data['categories_sheet'])]
    context.user_data['tags_sheet'] = 0

    text = "Выберите категорию"

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def categories_and_tags_update_tags_menu(update: Update, context: CallbackContext):
    sheets = await categories_and_tags_get_tags_sheets(update, context)
    sheet = sheets[int(context.user_data['tags_sheet'])]

    category = Category(id=int(context.user_data['category_id']))
    text = "Выберите тег из категории " + category.name

    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def categories_and_tags_send_tags_menu(update: Update, context: CallbackContext):
    sheets = await categories_and_tags_get_tags_sheets(update, context)
    context.user_data['tags_sheet'] = 0
    sheet = sheets[int(context.user_data['tags_sheet'])]

    category = Category(id=int(context.user_data['category_id']))
    text = "Выберите тег из категории " + category.name

    message =await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message

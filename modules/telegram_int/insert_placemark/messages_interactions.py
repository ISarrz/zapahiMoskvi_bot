from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from modules.telegram_int.insert_placemark.sheets_generators import placemark_inserter_get_categories_sheets
from modules.telegram_int.insert_placemark.sheets_generators import placemark_inserter_get_tags_sheets


async def placemark_inserter_update_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=("Нажмите на значок скрепки и найдите кнопку «Геопозиция», чтобы отправить метку. "
              "Заметьте, Вы можете двигать карту, чтобы уточнить местоположение, которым хотите поделиться."),
        reply_markup=None
    )


async def placemark_inserter_send_menu(update: Update, context: CallbackContext):
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Нажмите на значок скрепки и найдите кнопку «Геопозиция», чтобы отправить метку. "
              "Заметьте, Вы можете двигать карту, чтобы уточнить местоположение, которым хотите поделиться."),
        reply_markup=None
    )

    context.user_data['message'] = message


async def placemark_inserter_send_categories_menu(update: Update, context: CallbackContext):
    context.user_data['tags_sheet'] = 0
    context.user_data['categories_sheet'] = 0
    sheets = await placemark_inserter_get_categories_sheets(update, context)
    sheet = sheets[0]

    text = ("Добавьте тег — краткую характеристику запаха. Это как ноты в парфюме, но только те, "
            "которые наиболее часто можно встретить в городе. Для удобства мы разбили теги на условные категории.\n\n"
            "Можно добавить от одного до трех тегов или пропустить шаг, если ничего не подошло.\n\n"
            "Думаете, что тега для вашего запаха очень не хватает? Предложите свой, нажав на «Добавить тег»!")

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )

    context.user_data['message'] = message


async def placemark_inserter_update_categories_menu(update: Update, context: CallbackContext):
    sheets = await placemark_inserter_get_categories_sheets(update, context)
    sheet = sheets[int(context.user_data['categories_sheet'])]
    context.user_data['tags_sheet'] = 0

    text = ("Добавьте тег — краткую характеристику запаха. Это как ноты в парфюме, но только те, "
            "которые наиболее часто можно встретить в городе. Для удобства мы разбили теги на условные категории.\n\n"
            "Можно добавить от одного до трех тегов или пропустить шаг, если ничего не подошло.\n\n"
            "Думаете, что тега для вашего запаха очень не хватает? Предложите свой, нажав на «Добавить тег»!")

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

    text = ("Добавьте тег — краткую характеристику запаха. "
            "Это как ноты в парфюме, но только те, которые наиболее часто можно встретить в городе. "
            "Для удобства мы разбили теги на условные категории.\n\n"
            "Можно добавить от одного до трех тегов или пропустить шаг, если ничего не подошло. \n\n"
            "Думаете, что тега для вашего запаха очень не хватает? Предложите свой, нажав на «Добавить тег»!")

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

    text = ("Добавьте тег — краткую характеристику запаха. "
            "Это как ноты в парфюме, но только те, которые наиболее часто можно встретить в городе. "
            "Для удобства мы разбили теги на условные категории.\n\n"
            "Можно добавить от одного до трех тегов или пропустить шаг, если ничего не подошло. \n\n"
            "Думаете, что тега для вашего запаха очень не хватает? Предложите свой, нажав на «Добавить тег»!")

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message


async def placemark_inserter_update_tag_selected_menu(update: Update, context: CallbackContext):
    message = context.user_data['message']
    sheet = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Добавить еще тег", callback_data="add_more_tags"),
            InlineKeyboardButton(text="Отправить метку", callback_data="submit_placemark"),
        ]
    ])

    tags_count = len(context.user_data.get("tags", []))
    text = f"Тег выбран. Выбрано тегов: {tags_count}/3. Хотите добавить еще один?"

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup=sheet
    )


async def placemark_inserter_send_tag_selected_menu(update: Update, context: CallbackContext):
    sheet = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Добавить еще тег", callback_data="add_more_tags"),
            InlineKeyboardButton(text="Отправить метку", callback_data="submit_placemark"),
        ]
    ])

    tags_count = len(context.user_data.get("tags", []))
    text = f"Тег добавлен. Выбрано тегов: {tags_count}/3. Хотите добавить еще один?"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=sheet
    )
    context.user_data['message'] = message


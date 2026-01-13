from telegram.ext import CallbackContext, ConversationHandler
from modules.logger.logger import async_logger
from modules.telegram_int.constants import *
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.telegram_int.categories_and_tags.sheets_generators import (
    categories_and_tags_get_categories_sheets,
    categories_and_tags_get_tags_sheets
)
from modules.telegram_int.categories_and_tags.messages_interactions import (
    categories_and_tags_update_categories_menu,
    categories_and_tags_update_tags_menu,
    categories_and_tags_send_categories_menu,
    categories_and_tags_send_tags_menu
)
from modules.database.user.user import User
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag


@async_logger
async def categories_and_tags_handler(update: Update, context: CallbackContext):
    user = User(telegram_id=update.effective_user.id)
    if user.role != "admin":
        text = ("Привет! Это бот, отслеживающий запахи Москвы. "
                "Здесь вы можете оставить отзывы на ароматы, которые услышали в разных районах города. "
                "Попробуйте прислушаться к запахам вокруг и опишите их, а если возникнут затруднения — обратитесь к тегам, "
                "готовым нотам, разбитым на категории."
                "\n\nЧтобы добавить первый ольфакторный отзыв, нажмите кнопку «Добавить метку».")

        await update.message.reply_text(
            text=text
        )

        return MAIN_MENU_HANDLER

    context.user_data['tags_sheet'] = 0
    context.user_data['categories_sheet'] = 0
    await categories_and_tags_send_categories_menu(update, context)

    return CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER


@async_logger
async def categories_and_tags_categories_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        sheets = await categories_and_tags_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] -= 1
        context.user_data['categories_sheet'] += len(sheets)
        context.user_data['categories_sheet'] %= len(sheets)

        await categories_and_tags_update_categories_menu(update, context)

        return CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await categories_and_tags_get_categories_sheets(update, context)
        context.user_data['categories_sheet'] += 1
        context.user_data['categories_sheet'] %= len(sheets)

        await categories_and_tags_update_categories_menu(update, context)

        return CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER

    elif income == ADD:
        message = context.user_data['message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название категории",
            reply_markup=None
        )

        return CATEGORIES_AND_TAGS_INSERT_CATEGORY_MENU_HANDLER

    else:
        context.user_data['category_id'] = int(income)
        await categories_and_tags_update_tags_menu(update, context)

        return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER


@async_logger
async def categories_and_tags_insert_category_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    Category.safe_insert(name=name, user_id=user.id, status="approved")

    await categories_and_tags_send_categories_menu(update, context)

    return CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER


@async_logger
async def categories_and_tags_edit_category_handler(update: Update, context: CallbackContext):
    name = update.message.text
    category = Category(id=int(context.user_data['category_id']))
    category.name = name

    await categories_and_tags_send_tags_menu(update, context)

    return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER


@async_logger
async def categories_and_tags_delete_category_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        category = Category(id=int(context.user_data['category_id']))
        category.delete()

    await categories_and_tags_update_categories_menu(update, context)

    return CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER


@async_logger
async def categories_and_tags_tags_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await categories_and_tags_update_categories_menu(update, context)

        return CATEGORIES_AND_TAGS_CATEGORIES_MENU_HANDLER

    elif income == LEFT_ARROW:
        sheets = await categories_and_tags_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)

        await categories_and_tags_update_tags_menu(update, context)

        return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await categories_and_tags_get_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)

        await categories_and_tags_update_tags_menu(update, context)

        return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER


    elif income == DELETE:
        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]

        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']
        category = Category(id=int(context.user_data['category_id']))

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Удалить категорию " + category.name + "?",
            reply_markup=reply_markup
        )

        return CATEGORIES_AND_TAGS_DELETE_CATEGORY_MENU_HANDLER

    elif income == EDIT:
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите новое название категории",
            reply_markup=None
        )

        return CATEGORIES_AND_TAGS_EDIT_CATEGORY_MENU_HANDLER

    elif income == ADD:
        message = context.user_data['message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название тега",
            reply_markup=None
        )

        return CATEGORIES_AND_TAGS_INSERT_TAG_MENU_HANDLER

    else:
        context.user_data['tag_id'] = int(income)
        sheet = [[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=EDIT, callback_data=EDIT),
            InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]]

        tag = Tag(id=int(context.user_data['tag_id']))
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Тег " + tag.name,
            reply_markup=reply_markup
        )

        return CATEGORIES_AND_TAGS_TAG_MENU_HANDLER


@async_logger
async def categories_and_tags_insert_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text

    user = User(telegram_id=int(update.effective_user.id))
    tag = Tag.safe_insert(name=name, user_id=user.id, status="approved")
    category = Category(id=int(context.user_data['category_id']))
    tag.insert_category(category)

    await categories_and_tags_send_tags_menu(update, context)

    return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER


@async_logger
async def categories_and_tags_tag_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await categories_and_tags_update_tags_menu(update, context)

        return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER

    elif income == EDIT:
        message = context.user_data['message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите название тега",
            reply_markup=None
        )

        return CATEGORIES_AND_TAGS_EDIT_TAG_HANDLER

    elif income == DELETE:
        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]

        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']
        tag = Tag(id=int(context.user_data['tag_id']))

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Удалить тег " + tag.name + "?",
            reply_markup=reply_markup
        )

        return CATEGORIES_AND_TAGS_DELETE_TAG_MENU_HANDLER

    return ConversationHandler.END


@async_logger
async def categories_and_tags_edit_tag_handler(update: Update, context: CallbackContext):
    name = update.message.text
    tag = Tag(id=int(context.user_data['tag_id']))
    tag.name = name

    sheet = [[
        InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
        InlineKeyboardButton(text=EDIT, callback_data=EDIT),
        InlineKeyboardButton(text=DELETE, callback_data=DELETE),
    ]]

    tag = Tag(id=int(context.user_data['tag_id']))
    reply_markup = InlineKeyboardMarkup(sheet)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Тег " + tag.name,
        reply_markup=reply_markup
    )
    context.user_data['message'] = message
    return CATEGORIES_AND_TAGS_TAG_MENU_HANDLER


@async_logger
async def categories_and_tags_delete_tag_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))
        tag.delete()
        await categories_and_tags_update_tags_menu(update, context)

        return CATEGORIES_AND_TAGS_TAGS_MENU_HANDLER
    else:
        sheet = [[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text=EDIT, callback_data=EDIT),
            InlineKeyboardButton(text=DELETE, callback_data=DELETE),
        ]]

        tag = Tag(id=int(context.user_data['tag_id']))
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']

        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Тег " + tag.name,
            reply_markup=reply_markup
        )

        return CATEGORIES_AND_TAGS_TAG_MENU_HANDLER

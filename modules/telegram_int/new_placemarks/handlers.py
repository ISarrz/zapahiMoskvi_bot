from telegram.ext import CallbackContext, ConversationHandler
from modules.database.user.user import User
from modules.telegram_int.constants import *

from modules.telegram_int.new_placemarks.sheets_generators import (
    new_placemarks_get_placemarks_sheets,
    new_placemarks_get_placemark_new_tags_sheets
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from modules.telegram_int.new_placemarks.messages_interactions import (
    new_placemarks_update_placemarks_menu,
    new_placemarks_update_placemark_menu,
    new_placemarks_update_placemark_edit_menu,
    new_placemarks_send_placemark_edit_menu,
    new_placemarks_update_tags_menu,
    new_placemarks_update_tag_menu,
    new_placemarks_send_tag_menu,
    new_placemarks_send_placemarks_menu,
    new_placemarks_send_tag_categories_menu,
    new_placemarks_update_tag_categories_menu
)
# from modules.telegram_int.
from modules.database.placemark.tag import Tag
from modules.telegram_int.new_placemarks.support_functions import get_address
from modules.database.placemark.placemark import Placemark


async def new_placemarks_handler(update: Update, context: CallbackContext):
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

    context.user_data['new_placemarks_sheet'] = 0
    await new_placemarks_send_placemarks_menu(update, context)
    return NEW_PLACEMARKS_HANDLER


async def new_placemarks_selector_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == LEFT_ARROW:
        context.user_data['new_placemarks_sheet'] -= 1
        sheets = new_placemarks_get_placemarks_sheets()
        context.user_data['new_placemarks_sheet'] += len(sheets)
        context.user_data['new_placemarks_sheet'] %= len(sheets)

        await new_placemarks_update_placemarks_menu(update, context)

        return NEW_PLACEMARKS_HANDLER

    elif income == RIGHT_ARROW:
        context.user_data['new_placemarks_sheet'] += 1
        sheets = new_placemarks_get_placemarks_sheets()
        context.user_data['new_placemarks_sheet'] %= len(sheets)

        await new_placemarks_update_placemarks_menu(update, context)

        return NEW_PLACEMARKS_HANDLER



    else:
        context.user_data['placemark_changed'] = False
        context.user_data['selected_placemark_id'] = int(income)
        await new_placemarks_update_placemark_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_MENU_HANDLER


async def new_placemarks_placemark_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await new_placemarks_update_placemarks_menu(update, context)

        return NEW_PLACEMARKS_HANDLER

    elif income == SUBMIT:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))

        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]
        if sheet:
            reply_markup = InlineKeyboardMarkup(sheet)
        else:
            reply_markup = None

        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Принять отзыв " + placemark.address + "?",
            reply_markup=reply_markup
        )

        return NEW_PLACEMARKS_PLACEMARK_APPROVE_HANDLER

    elif income == EDIT:
        await new_placemarks_update_placemark_edit_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER

    return ConversationHandler.END


async def new_placemarks_placemark_approve_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
        if context.user_data['placemark_changed']:
            user = User(id=placemark.user_id)
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text="Ваша метка " + placemark.address + " была изменина и принята модерацией.",
                reply_markup=None
            )
        placemark.approve()
        for tag in placemark.tags:
            tag.approve()

        await new_placemarks_update_placemarks_menu(update, context)
        return NEW_PLACEMARKS_HANDLER

    else:
        await new_placemarks_update_placemark_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_MENU_HANDLER


async def new_placemarks_placemark_edit_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))

    if income == BACK_ARROW:
        await new_placemarks_update_placemark_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_MENU_HANDLER

    elif income == "tags":
        context.user_data['tags_sheet'] = 0
        await new_placemarks_update_tags_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER

    elif income == "address":
        message = context.user_data["message"]
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="`" + placemark.address + "`" + "\n\nВведите адресс",
            reply_markup=None,
            parse_mode="MarkdownV2"
        )

        return NEW_PLACEMARKS_PLACEMARK_EDIT_ADDRESS_HANDLER

    elif income == "description":
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="`" + placemark.description + "`" + "\n\nВведите описание",
            reply_markup=None,
            parse_mode="MarkdownV2"
        )

        return NEW_PLACEMARKS_PLACEMARK_EDIT_DESCRIPTION_HANDLER

    elif income == "geotag":
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Отправьте геометку",
            reply_markup=None
        )

        return NEW_PLACEMARKS_PLACEMARK_EDIT_GEOTAG_HANDLER

    elif income == DELETE:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))

        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Удалить отзыв " + placemark.address + "?",
            reply_markup=reply_markup
        )

        return NEW_PLACEMARKS_PLACEMARK_DELETE_HANDLER

    return ConversationHandler.END


async def new_placemarks_placemark_edit_location_handler(update: Update, context: CallbackContext):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    placemark = Placemark(id=int(context.user_data["selected_placemark_id"]))

    placemark.latitude = latitude
    placemark.longitude = longitude
    placemark.address = get_address(latitude, longitude)

    context.user_data["placemark_changed"] = True

    # Отправляем сообщение об успешном изменении
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Геолокация успешно изменена!",
        reply_markup=None
    )

    await new_placemarks_send_placemark_edit_menu(update, context)
    return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER


async def new_placemarks_placemark_edit_address_handler(update: Update, context: CallbackContext):
    address = update.message.text
    placemark = Placemark(id=int(context.user_data["selected_placemark_id"]))
    placemark.address = address

    context.user_data["placemark_changed"] = True

    # Отправляем сообщение об успешном изменении
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Адрес успешно изменен!",
        reply_markup=None
    )

    await new_placemarks_send_placemark_edit_menu(update, context)
    return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER


async def new_placemarks_placemark_edit_description_handler(update: Update, context: CallbackContext):
    description = update.message.text
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    placemark.description = description

    context.user_data['placemark_changed'] = True

    # Отправляем сообщение об успешном изменении
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Описание успешно изменено!",
        reply_markup=None
    )

    await new_placemarks_send_placemark_edit_menu(update, context)
    return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER


async def new_placemarks_placemark_delete_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        placemark = Placemark(id=int(context.user_data['selected_placemark_id']))

        placemark.reject()
        await new_placemarks_update_placemarks_menu(update, context)
        return NEW_PLACEMARKS_HANDLER

    else:
        await new_placemarks_update_placemark_edit_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER


async def new_placemarks_tags_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await new_placemarks_update_placemark_edit_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER

    elif income == LEFT_ARROW:
        sheets = await new_placemarks_get_placemark_new_tags_sheets(update, context)
        context.user_data['tags_sheet'] -= 1
        context.user_data['tags_sheet'] += len(sheets)
        context.user_data['tags_sheet'] %= len(sheets)
        await new_placemarks_update_tags_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER

    elif income == RIGHT_ARROW:
        sheets = await new_placemarks_get_placemark_new_tags_sheets(update, context)
        context.user_data['tags_sheet'] += 1
        context.user_data['tags_sheet'] %= len(sheets)
        await new_placemarks_update_tags_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER

    else:
        context.user_data['tag_id'] = int(income)
        await new_placemarks_update_tag_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER


async def new_placemarks_tag_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == EDIT:
        tag = Tag(id=int(context.user_data['tag_id']))

        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Введите новое название для тега " + tag.name,
            reply_markup=None
        )

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_EDIT_HANDLER

    elif income == BACK_ARROW:
        await new_placemarks_update_placemark_edit_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_EDIT_HANDLER

    elif income == "category":
        await new_placemarks_update_tag_categories_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_CATEGORY_HANDLER

    elif income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))

        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']
        await context.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="Добавить тег " + tag.name + "?",
            reply_markup=reply_markup
        )

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_APPROVE_HANDLER

    elif income == DELETE:
        tag = Tag(id=int(context.user_data['tag_id']))

        sheet = [[
            InlineKeyboardButton(text=SUBMIT, callback_data=SUBMIT),
            InlineKeyboardButton(text=CANCEL, callback_data=CANCEL),
        ]]
        reply_markup = InlineKeyboardMarkup(sheet)
        message = context.user_data['message']
        if tag.status == "approved":
            await context.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text="Открепить тег " + tag.name + "?",
                reply_markup=reply_markup
            )

        else:
            await context.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text="Удалить тег " + tag.name + "?",
                reply_markup=reply_markup
            )

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_DELETE_HANDLER

    return ConversationHandler.END


async def new_placemarks_tag_edit_handler(update: Update, context: CallbackContext):
    name = update.message.text
    tag = Tag(id=int(context.user_data['tag_id']))
    tag.name = name

    await new_placemarks_send_tag_menu(update, context)

    return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER


async def new_placemarks_delete_tag_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))
        if tag.status == "approved":
            placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
            placemark.delete_tag(tag)

        else:
            tag.delete()

        await new_placemarks_update_tags_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER

    else:
        await new_placemarks_update_tag_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER


async def new_placemarks_approve_tag_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == SUBMIT:
        tag = Tag(id=int(context.user_data['tag_id']))
        tag.approve()
        await new_placemarks_update_tags_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_NEW_TAGS_HANDLER

    else:
        await new_placemarks_update_tag_menu(update, context)

        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER


async def new_placemarks_tag_category_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data

    if income == BACK_ARROW:
        await new_placemarks_update_tag_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER

    elif income == "no_category":
        # Удалить тег из всех категорий
        tag = Tag(id=int(context.user_data['tag_id']))
        category_id = tag.category_id
        if category_id != -1:
            from modules.database.placemark.category import Category
            category = Category(id=category_id)
            tag.delete_category(category)

        await new_placemarks_update_tag_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER

    else:
        # Назначить тег в категорию
        from modules.database.placemark.category import Category
        tag = Tag(id=int(context.user_data['tag_id']))

        # Сначала удаляем из старой категории
        old_category_id = tag.category_id
        if old_category_id != -1:
            old_category = Category(id=old_category_id)
            tag.delete_category(old_category)

        # Добавляем в новую категорию
        new_category = Category(id=int(income))
        tag.insert_category(new_category)

        await new_placemarks_update_tag_menu(update, context)
        return NEW_PLACEMARKS_PLACEMARK_NEW_TAG_HANDLER

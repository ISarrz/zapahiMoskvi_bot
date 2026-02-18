from modules.database.placemark.placemark import Placemark
from modules.telegram_int.constants import *
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


from telegram.ext import CallbackContext
from modules.database.user.user import User
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag, TagNotFoundError



def edit_placemarks_get_placemarks_sheets(user: User):
    sheets = []
    if not user.placemarks:
        return [None]

    placemarks = [Placemark(id=placemark.id) for placemark in user.placemarks]
    cur_sheet = []

    for placemark in placemarks:
        if len(cur_sheet) >= MAX_SHEET_LENGTH:
            sheets.append(cur_sheet)
            cur_sheet = []

        cur_sheet.append([InlineKeyboardButton(text=placemark.description, callback_data=placemark.id)])

    if cur_sheet:
        sheets.append(cur_sheet)

    for i in range(len(sheets)):
        sheet = sheets[i]
        if len(sheets) > 1:
            sheet.append([
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW)
            ])


    return sheets


async def edit_placemarks_get_categories_sheets(update: Update, context: CallbackContext):
    user = User(telegram_id=int(update.effective_user.id))
    categories = Category.approved_and_user(user.id)
    sheets = []
    selected_category_ids = set()
    for tag_id in context.user_data.get("tags", []):
        try:
            tag = Tag(id=tag_id)
        except TagNotFoundError:
            continue

        if tag.category_id != -1:
            selected_category_ids.add(tag.category_id)

    for category in categories:
        if not sheets or len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH:
            sheets.append([])

        text = category.name
        if category.id in selected_category_ids:
            text += " " + SUBMIT

        sheets[-1].append([InlineKeyboardButton(text=text, callback_data=category.id)])

    # Проверяем, были ли изменения
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    original_tag_ids = set(tag.id for tag in placemark.tags)
    current_tag_ids = set(context.user_data.get("tags", []))
    has_changes = original_tag_ids != current_tag_ids

    for i in range(len(sheets)):
        if len(sheets) > 1:
            if has_changes:
                sheets[i].append([
                    InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                    InlineKeyboardButton(text="Подтвердить", callback_data="skip"),
                    InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
                ])
            else:
                sheets[i].append([
                    InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                    InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
                ])
        else:
            if has_changes:
                sheets[i].append([
                    InlineKeyboardButton(text="Подтвердить", callback_data="skip"),
                ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets


async def edit_placemarks_get_tags_sheets(update: Update, context: CallbackContext):
    category_id = context.user_data.get('category_id')

    category = Category(id=int(category_id))
    tags = []
    user = User(telegram_id=int(update.effective_user.id))
    for tag in category.tags:
        if tag.status == "approved" or tag.user_id == user.id:
            tags.append(tag)

    sheets = []
    for tag in tags:
        if not sheets:
            sheets.append([[]])
        if len(sheets[-1]) >= MAX_CATEGORIES_SHEET_LENGTH and len(sheets[-1][-1]) >= 2:
            sheets.append([[]])

        if len(sheets[-1][-1]) >= 2:
            sheets[-1].append([])

        text  = tag.name
        if tag.id in context.user_data["tags"]:
            text += " " + SUBMIT

        sheets[-1][-1].append(InlineKeyboardButton(text=text, callback_data=tag.id))

    # Проверяем, были ли изменения
    placemark = Placemark(id=int(context.user_data['selected_placemark_id']))
    original_tag_ids = set(tag.id for tag in placemark.tags)
    current_tag_ids = set(context.user_data.get("tags", []))
    has_changes = original_tag_ids != current_tag_ids

    for i in range(len(sheets)):
        # Добавляем кнопку "Добавить тег"
        sheets[i].append([
            InlineKeyboardButton(text="Добавить тег", callback_data=ADD),
        ])

        if len(sheets) > 1:
            sheets[i].append([
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text="Пропустить" if not context.user_data.get("tags") else "Подтвердить", callback_data="skip"),
                InlineKeyboardButton(text=LEFT_ARROW, callback_data=LEFT_ARROW),
                InlineKeyboardButton(text=RIGHT_ARROW, callback_data=RIGHT_ARROW),
            ])
        else:
            sheets[i].append([
                InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
                InlineKeyboardButton(text="Пропустить" if not context.user_data.get("tags") else "Подтвердить", callback_data="skip"),
            ])

        sheets[i] = InlineKeyboardMarkup(sheets[i])

    if not sheets:
        sheets.append([[
            InlineKeyboardButton(text="Добавить тег", callback_data=ADD),
        ],[
            InlineKeyboardButton(text=BACK_ARROW, callback_data=BACK_ARROW),
            InlineKeyboardButton(text="Пропустить" if not context.user_data.get("tags") else "Подтвердить", callback_data="skip"),
        ]])
        sheets[0] = InlineKeyboardMarkup(sheets[0])

    return sheets

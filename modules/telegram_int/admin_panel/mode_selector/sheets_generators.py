from telegram import InlineKeyboardButton


def mode_selector_get_menu_sheet():
    sheet = [
        [InlineKeyboardButton(text="Новые отзывы", callback_data="new placemarks")],
        [InlineKeyboardButton(text="Новые теги", callback_data="new tags")],
        [InlineKeyboardButton(text="Принятые отзывы", callback_data="approved placemarks")],
        [InlineKeyboardButton(text="Добавить категории и теги", callback_data="add categories and tags")],
    ]

    return sheet

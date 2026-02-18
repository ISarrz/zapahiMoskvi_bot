"""
Модуль для работы с клавиатурами Telegram бота
"""
from telegram import ReplyKeyboardMarkup
from modules.database.user.user import User


def get_main_keyboard(user: User = None, user_id: int = None, telegram_id: int = None):
    """
    Возвращает основную клавиатуру для пользователя

    Args:
        user: Объект пользователя User
        user_id: ID пользователя в БД
        telegram_id: Telegram ID пользователя
    """
    # Получаем объект пользователя если не передан
    if not user:
        if telegram_id:
            user = User(telegram_id=telegram_id)
        elif user_id:
            user = User(id=user_id)
        else:
            # Если ничего не передано, создаём клавиатуру без админских кнопок
            reply_keyboard = [
                ["Добавить метку", "Все метки"],
                ["Мои метки", "Напоминания"],
                ["О нас"],
            ]
            return ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=False, input_field_placeholder="Выберите раздел"
            )

    reply_keyboard = [
        ["Добавить метку", "Все метки"],
        ["Мои метки", "Напоминания"],
        ["О нас"],
    ]

    if user.role == "admin":
        reply_keyboard.append(["Новые метки", "Категории и теги", "Принятые метки"])

    return ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=False, input_field_placeholder="Выберите раздел"
    )


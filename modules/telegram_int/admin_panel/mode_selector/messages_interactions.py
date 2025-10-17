from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from modules.telegram_int.admin_panel.mode_selector.sheets_generators import mode_selector_get_menu_sheet


async def mode_selector_send_menu(update: Update, context: CallbackContext):
    sheet = mode_selector_get_menu_sheet()
    reply_markup = InlineKeyboardMarkup(sheet)



    message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                             text="Панель администратора",
                                             reply_markup=reply_markup)

    context.user_data['admin_panel_message'] = message


async def mode_selector_update_menu(update: Update, context: CallbackContext):
    sheet = mode_selector_get_menu_sheet()
    reply_markup = InlineKeyboardMarkup(sheet)

    message = context.user_data['admin_panel_message']

    await context.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="Панель администратора",
        reply_markup=reply_markup
    )

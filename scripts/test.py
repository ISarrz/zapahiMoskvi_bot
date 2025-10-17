#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


async def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [["1", "2"]]

    await update.message.reply_text(
        text="start message",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="my keyboard"
        ),
    )

    return 0


async def scene1(update: Update, context: CallbackContext) -> int:
    sheet = [[
        InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
    ]]
    reply_markup = InlineKeyboardMarkup(sheet)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="scene 1",
        reply_markup=reply_markup
    )

    return 1


async def scene2(update: Update, context: CallbackContext) -> int:
    sheet = [[
        InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
    ]]
    reply_markup = InlineKeyboardMarkup(sheet)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="scene 2",
        reply_markup=reply_markup
    )

    return 2


async def scene1_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"scene1 {income}",
        reply_markup=None
    )


async def scene2_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    income = query.data
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"scene2 {income}",
        reply_markup=None
    )


async def cancel(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token("7739506665:AAFD3MuB1TViwokJYew5pcA8NvMPlpC1K3A").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            0: [
                MessageHandler(filters.Regex("(?i)^(1)$"), scene1),
                MessageHandler(filters.Regex("(?i)^(2)$"), scene2),
            ],
            1: [
                CallbackQueryHandler(scene1_handler),
                MessageHandler(filters.Regex("(?i)^(1)$"), scene1),
                MessageHandler(filters.Regex("(?i)^(2)$"), scene2),

            ],
            2: [
                CallbackQueryHandler(scene2_handler),
                MessageHandler(filters.Regex("(?i)^(1)$"), scene1),
                MessageHandler(filters.Regex("(?i)^(2)$"), scene2),
            ],

        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

from pyanaconda.argument_parsing import DESCRIPTION
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters, CallbackContext
)
from modules.logger.logger import logger, async_logger
from modules.database.user.user import User
from modules.database.placemark.placemark import Placemark
from modules.database.placemark.tag import Tag
from modules.database.placemark.category import Category

from modules.time.time import now
from geopy.geocoders import Nominatim

from modules.telegram_int.user_placemarks_menu.constants import *


def update_placemark(update: Update, context: CallbackContext):
    pass
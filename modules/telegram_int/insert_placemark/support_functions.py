from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from modules.database.user.user import User
from modules.database.placemark.tag import Tag

from modules.time.time import now
from geopy.geocoders import Nominatim
import html
from modules.telegram_int.keyboard import get_main_keyboard


def get_address(latitude: float, longitude: float):
    try:
        geolocator = Nominatim(user_agent="my_geocoder")

        location = geolocator.reverse((latitude, longitude), language="ru")
        res = []

        if location.raw["address"].get("suburb"):
            res.append(location.raw["address"]["suburb"])

        if location.raw["address"].get("road"):
            res.append(location.raw["address"]["road"])

        if location.raw["address"].get("house_number"):
            res.append(location.raw["address"]["house_number"])

        if not res:
            res.append("Неизвестно")

        address = "; ".join(res)

        return address
    
    except Exception as e:
        return "Неизвестно"



async def insert_user_placemark(update: Update, context: CallbackContext):
    tags = [Tag(id=tag_id) for tag_id in context.user_data["tags"]]
    user = User(telegram_id=update.effective_user.id)

    placemark = user.insert_placemark(datetime=now(), address=context.user_data["address"],
                                      latitude=context.user_data["latitude"],
                                      longitude=context.user_data["longitude"],
                                      description=context.user_data["description"])

    for tag in tags:
        placemark.insert_tag(tag=tag)

    address = html.escape(str(placemark.address))
    description = html.escape(str(placemark.description))
    tags_text = ", ".join(html.escape(tag.name) for tag in placemark.tags)
    datetime_text = html.escape(str(placemark.datetime))

    text = "📌 Ваша геометка и отзыв добавлены:\n\n"
    text += f"{address}\n"
    text += f"<i>{datetime_text}</i>\n\n"
    text += f"Описание: {description}\n"
    text += f"Теги: {tags_text}\n\n"
    text += "<i>Метка появится на карте, когда пройдет модерацию.</i>"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=get_main_keyboard(user),
        parse_mode="HTML"
    )

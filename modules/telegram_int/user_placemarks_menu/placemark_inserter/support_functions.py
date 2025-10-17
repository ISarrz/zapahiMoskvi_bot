from telegram import Update
from telegram.ext import CallbackContext
from modules.database.user.user import User
from modules.database.placemark.tag import Tag

from modules.time.time import now
from geopy.geocoders import Nominatim


def get_address(latitude: int, longitude: int):
    geolocator = Nominatim(user_agent="my_geocoder")

    location = geolocator.reverse((latitude, longitude), language="ru")
    res = []

    if location.raw["address"].get("suburb"):
        res.append(location.raw["address"]["suburb"])

    if location.raw["address"].get("road"):
        res.append(location.raw["address"]["road"])

    if location.raw["address"].get("house_number"):
        res.append(location.raw["address"]["house_number"])

    if location.raw["address"].get("postcode"):
        res.append(location.raw["address"]["postcode"])

    if not res:
        res.append("Неизвестно")

    address = "; ".join(res)

    return address



async def insert_user_placemark(update: Update, context: CallbackContext):
    tags = [Tag(id=tag_id) for tag_id in context.user_data["tags"]]
    user = User(telegram_id=update.effective_user.id)

    placemark = user.insert_placemark(datetime=now(), address=context.user_data["address"],
                                      latitude=context.user_data["latitude"],
                                      longitude=context.user_data["longitude"],
                                      description=context.user_data["description"])

    for tag in tags:
        placemark.insert_tag(tag=tag)
    text = "Ваша геометка добавлена:\n"
    text += "Адресс: " + placemark.address + "\n"
    text += "Долгота: " + placemark.latitude + "\n"
    text += "Широта: " + placemark.longitude + "\n"
    text += "Описание: " + placemark.description + "\n"
    text += "Теги: " + ', '.join([tag.name for tag in tags]) + "\n"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=None
    )

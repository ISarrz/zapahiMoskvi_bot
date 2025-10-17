from geopy.geocoders import Nominatim


def get_address(latitude: float, longitude: float):
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

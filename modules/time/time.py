from datetime import datetime
from zoneinfo import ZoneInfo


def now():
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
    formatted = moscow_time.strftime("%d.%m.%Y %H:%M")

    return formatted

def now_data():
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
    return moscow_time
from modules.config.paths import config_path, telegram_messages_path, telegram_data_path
import json
import os


def get_config():
    with open(config_path) as f:
        response = json.load(f)

    return response


def get_config_field(field):
    return get_config()[field]


def get_telegram_message(name):
    with open(os.path.join(telegram_messages_path, name + ".txt")) as f:
        return f.read()


def get_notification_message(user_id: int):
    with open(telegram_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get(str(user_id))


def set_notification_message(user_id: int, message):
    with open(telegram_data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        data[user_id] = message

    with open(telegram_data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
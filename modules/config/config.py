from modules.config.paths import config_path, telegram_messages_path
import json
import os


def get_config():
    with open(config_path) as f:
        response = json.load(f)

    return response


def get_config_field(field):
    return get_config()[field]

def get_telegram_message(name):
    with open(os.path.join(telegram_messages_path, name+".txt")) as f:
        return f.read()
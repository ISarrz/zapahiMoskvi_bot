import json
from modules.config.paths import config_path


def initialize_config():
    config = {
        "telegram_api_token": input("Enter Telegram API token: "),
        "admins_chat_id": input("Enter admins chat id: "),
        "logs_chat_id": input("Enter logs chat id: "),

    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    initialize_config()

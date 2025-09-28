import json
import modules.database
from modules.config.paths import config_path


def initialize_config():
    config = {
        "telegram_api_token": input("Enter Telegram API token: "),

    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    initialize_config()

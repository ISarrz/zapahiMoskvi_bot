from __future__ import annotations

from typing import List
from dataclasses import dataclass
from datetime import datetime
from modules.database.database.database import DB
from modules.database.geotag.geotag import Geotag, DbGeotag


class UserNotFoundError(Exception):
    def __str__(self) -> str:
        return "User not found"


class UserAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "User not found"


class InvalidUserArgumentsError(Exception):
    def __str__(self) -> str:
        return "Invalid user arguments"


@dataclass
class DbUser():
    id: int
    telegram_id: int


class UserFetcher:
    @staticmethod
    def fetch_all() -> List[DbUser]:
        return UserFetcher.constructor(DB.fetch_many(DB.users_table_name))

    @staticmethod
    def fetch_by_telegram_id(telegram_id: int):
        return UserFetcher.constructor(DB.fetch_one(DB.users_table_name, telegram_id=telegram_id))

    @staticmethod
    def fetch_by_id(id: int) -> DbUser:
        return UserFetcher.constructor(DB.fetch_one(DB.users_table_name, id=id))

    @staticmethod
    def constructor(info) -> DbUser | List[DbUser] | None:
        if not info:
            return None

        if isinstance(info, list):
            return [UserFetcher.constructor(user_info) for user_info in info]

        else:
            return DbUser(id=info["id"], telegram_id=info["telegram_id"])


class UserDeleter:
    @staticmethod
    def delete(user: DbUser):
        DB.delete_one(DB.users_table_name, id=user.id)


class UserInserter:
    @staticmethod
    def insert(telegram_id: int):
        DB.insert_one(DB.users_table_name, telegram_id=telegram_id)
        user = UserFetcher.fetch_by_telegram_id(telegram_id=telegram_id)

    @staticmethod
    def insert_geotag(user_id, geotag, about):
        DB.insert_one(DB.users_geotags_table_name, user_id=user_id, geotag=geotag, about=about)


class UserUpdater:
    pass
    # @staticmethod
    # def update_notifications(user: DbUser, notifications_state: int):
    #     DB.update_one(DB.users_notifications_table_name, dict(user_id=user.id), dict(value=notifications_state))


class User:
    _user: DbUser

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._user = UserFetcher.fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"telegram_id"}:
            self._user = UserFetcher.fetch_by_telegram_id(kwargs["telegram_id"])

        elif kwargs_keys == {"db_user"}:
            self._user = kwargs["db_user"]

        else:
            raise InvalidUserArgumentsError

        if not self._user:
            raise UserNotFoundError

    @staticmethod
    def all():
        users = UserFetcher.fetch_all()

        if users:
            return [User(db_user=user_info) for user_info in users]

        return []

    @property
    def id(self) -> int:
        return self._user.id

    @property
    def telegram_id(self) -> int:
        return self._user.telegram_id

    @property
    def geotags(self) -> list[DbGeotag]:
        return Geotag.user_geotags(user_id=self.id)

    @staticmethod
    def safe_insert(telegram_id: int):
        try:
            User.insert(telegram_id=telegram_id)
        except UserAlreadyExistsError:
            pass

    @staticmethod
    def insert(telegram_id: int) -> User:
        try:
            User(telegram_id=telegram_id)

            raise UserAlreadyExistsError

        except UserNotFoundError:
            UserInserter.insert(telegram_id=telegram_id)

            return User(telegram_id=telegram_id)

    def delete(self):
        UserDeleter.delete(self._user)

    def insert_geotag(self, geotag, about):
        Geotag.insert(self.id, geotag, about)

    def __str__(self):
        return f"id: {self.id}, telegram_id: {self.telegram_id}"


if __name__ == "__main__":
    pass

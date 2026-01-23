from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database.database.database import DB
from modules.database.placemark.placemark import Placemark, DbPlacemark
from modules.database.user.notification import DbNotification, Notification


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
class DbUser:
    id: int
    telegram_id: int
    role: str


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
            return DbUser(**dict(info))


class UserDeleter:
    @staticmethod
    def delete(user: DbUser):
        DB.delete_one(DB.users_table_name, id=user.id)


class UserInserter:
    @staticmethod
    def insert(telegram_id: int, role="user"):
        DB.insert_one(DB.users_table_name, telegram_id=telegram_id, role=role)
        user = UserFetcher.fetch_by_telegram_id(telegram_id=telegram_id)


class UserUpdater:
    pass

    @staticmethod
    def update_role(user_id: int, role: str):
        DB.update_one(DB.users_table_name, {"id": user_id}, {"role": role})


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
    def placemarks(self) -> list[DbPlacemark]:
        return Placemark.user_placemarks(user_id=self.id)

    @property
    def notifications(self) -> list[DbNotification]:
        x = Notification.user_notifications(user_id=self.id)
        if not x:
            return []
        return x

    @property
    def role(self) -> str:
        return self._user.role

    def give_admin_role(self):
        UserUpdater.update_role(self.id, "admin")

    def give_user_role(self):
        UserUpdater.update_role(self.id, "user")

    @staticmethod
    def safe_insert(telegram_id: int, role="user"):
        try:
            User.insert(telegram_id=telegram_id, role=role)
        except UserAlreadyExistsError:
            pass

    @staticmethod
    def insert(telegram_id: int, role="user") -> User:
        try:
            User(telegram_id=telegram_id)

            raise UserAlreadyExistsError

        except UserNotFoundError:
            UserInserter.insert(telegram_id=telegram_id, role=role)

            return User(telegram_id=telegram_id)

    def delete(self):
        UserDeleter.delete(self._user)

    def insert_placemark(self, datetime: str, address: str, latitude: str, longitude: str, description: str,
                         status="pending"):
        return Placemark.insert(self.id, datetime, address, latitude, longitude, description, status)

    def __str__(self):
        return f"id: {self.id}, telegram_id: {self.telegram_id}"


if __name__ == "__main__":
    pass

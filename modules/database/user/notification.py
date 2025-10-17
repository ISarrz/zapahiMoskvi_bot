from __future__ import annotations

from typing import List
from dataclasses import dataclass

from modules.database.database.database import DB
from datetime import datetime


class NotificationNotFoundError(Exception):
    def __str__(self) -> str:
        return "Notification not found"


class NotificationAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "Notification not found"


class InvalidNotificationArgumentsError(Exception):
    def __str__(self) -> str:
        return "Invalid notification arguments"


@dataclass
class DbNotification:
    id: int
    user_id: int
    weekday: int
    time: str


class NotificationFetcher:
    @staticmethod
    def fetch_all() -> List[DbNotification]:
        return NotificationFetcher.constructor(DB.fetch_many(DB.users_table_name))

    @staticmethod
    def fetch_by_user_id_weekday_and_time(user_id: int, weekday: int, time: str):
        return NotificationFetcher.constructor(
            DB.fetch_many(DB.users_notifications_table_name, user_id=user_id, weekday=weekday, time=time))

    @staticmethod
    def fetch_by_user_id(user_id: int):
        return NotificationFetcher.constructor(DB.fetch_many(DB.users_notifications_table_name, user_id=user_id))

    @staticmethod
    def fetch_by_id(id: int) -> DbNotification:
        return NotificationFetcher.constructor(DB.fetch_one(DB.users_notifications_table_name, id=id))

    @staticmethod
    def constructor(info) -> DbNotification | List[DbNotification] | None:
        if not info:
            return None

        if isinstance(info, list):
            return [NotificationFetcher.constructor(user_info) for user_info in info]

        else:
            return DbNotification(**dict(info))


class NotificationDeleter:
    @staticmethod
    def delete(notification: DbNotification):
        DB.delete_one(DB.users_notifications_table_name, id=notification.id)


class NotificationInserter:
    @staticmethod
    def insert(user_id: int, weekday: int, time: str):
        return DB.insert_one(DB.users_notifications_table_name, user_id=user_id, weekday=weekday, time=time)


class UserUpdater:
    pass
    # @staticmethod
    # def update_place(user: DbUser, notifications_state: int):
    #     DB.update_one(DB.users_notifications_table_name, dict(user_id=user.id), dict(value=notifications_state))


class Notification:
    _notification: DbNotification

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._notification = NotificationFetcher.fetch_by_id(kwargs["id"])

        elif kwargs_keys == {"db_notification"}:
            self._notification = kwargs["db_notification"]

        elif "user_id" in kwargs_keys and "weekday" in kwargs_keys and "time" in kwargs:
            self._notification = NotificationFetcher.fetch_by_user_id_weekday_and_time(kwargs["user_id"],
                                                                                       kwargs["weekday"],
                                                                                       kwargs["time"])
        else:
            raise InvalidNotificationArgumentsError

        if not self._notification:
            raise NotificationNotFoundError

    @staticmethod
    def all():
        users = NotificationFetcher.fetch_all()

        if users:
            return [Notification(db_notification=notification_info) for notification_info in users]

        return []

    @property
    def id(self) -> int:
        return self._notification.id

    @property
    def weekday(self) -> int:
        return self._notification.weekday

    @property
    def time(self) -> str:
        return self._notification.time

    @staticmethod
    def insert(user_id: int, weekday: int, time: str) -> Notification:
        try:
            Notification(user_id=user_id, weekday=weekday, time=time)

            raise NotificationAlreadyExistsError

        except NotificationNotFoundError:
            notification_id = NotificationInserter.insert(user_id=user_id, weekday=weekday, time=time)

            return Notification(id=notification_id)

    def delete(self):
        NotificationDeleter.delete(self._notification)

    @staticmethod
    def user_notifications(user_id: int) -> List[DbNotification]:
        return NotificationFetcher.fetch_by_user_id(user_id=user_id)

if __name__ == "__main__":
    pass

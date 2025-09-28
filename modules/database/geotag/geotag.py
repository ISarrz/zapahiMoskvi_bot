from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database.database.database import DB


class GeotagNotFoundError(Exception):
    def __str__(self) -> str:
        return "Group not found"


class GeotagAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "Group already exists"


class IncorrectGeotagArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect group arguments"


# database container structure
@dataclass
class DbGeotag:
    id: int
    user_id: int
    geotag: str
    about: str


class GeotagDeleter:
    @staticmethod
    def delete(geotag: DbGeotag):
        DB.delete_one(DB.users_geotags_table_name, id=geotag.id)


class GeotagUpdater:
    pass
    # @staticmethod
    # def update_name(group: DbGroup, name: str):
    #     DB.update_one(DB.groups_table_name, group.__dict__, {"name": name})


class GeotagFetcher:
    @staticmethod
    def fetch_all() -> List[DbGeotag]:
        return GeotagFetcher.constructor(DB.fetch_many(DB.users_geotags_table_name))

    @staticmethod
    def fetch_by_user_id(user_id: int):
        return GeotagFetcher.constructor(DB.fetch_many(DB.users_geotags_table_name, user_id=user_id))

    @staticmethod
    def fetch_by_id(id: int) -> DbGeotag:
        return GeotagFetcher.constructor(DB.fetch_one(DB.users_geotags_table_name, id=id))

    @staticmethod
    def fetch_by_geotag(geotag: str) -> DbGeotag:
        return GeotagFetcher.constructor(DB.fetch_one(DB.users_geotags_table_name, geotag=geotag))

    @staticmethod
    def constructor(info) -> DbGeotag | List[DbGeotag] | None:
        if not info:
            return None

        if isinstance(info, list):
            groups = [GeotagFetcher.constructor(group_info) for group_info in info]

            if groups:
                return groups

            return []

        else:
            return DbGeotag(**dict(info))


class GeotagInserter:
    @staticmethod
    def insert(user_id, geotag: str, about: str):
        return DB.insert_one(DB.users_geotags_table_name, user_id=user_id, geotag=geotag, about=about)


class Geotag:
    _geotag: DbGeotag

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._geotag = GeotagFetcher.fetch_by_id(kwargs.get("id"))

        elif kwargs_keys == {"geotag"}:
            self._geotag = GeotagFetcher.fetch_by_geotag(kwargs.get("geotag"))

        elif kwargs_keys == {"db_geotag"}:
            self._geotag = kwargs.get("db_geotag")

        else:
            raise IncorrectGeotagArgumentsError()

        if not self._geotag:
            raise GeotagNotFoundError

    @property
    def geotag(self) -> str:
        return self._geotag.geotag

    @property
    def user_id(self) -> int:
        return self._geotag.user_id


    @property
    def about(self) -> str:
        return self._geotag.about

    @property
    def id(self) -> int:
        return self._geotag.id

    @staticmethod
    def all() -> Geotag | List[Geotag]:
        groups = GeotagFetcher.fetch_all()

        if groups:
            return [Geotag(db_geotag=info) for info in groups]

        return []

    @staticmethod
    def user_geotags(user_id: int) -> List[DbGeotag]:
        return GeotagFetcher.fetch_by_user_id(user_id=user_id)

    @staticmethod
    def insert(user_id, geotag: str, about: str) -> Geotag:
        geotag_id = GeotagInserter.insert(user_id, geotag, about)

        return Geotag(id=geotag_id)

    def delete(self):
        GeotagDeleter.delete(self._geotag)


if __name__ == "__main__":
    pass

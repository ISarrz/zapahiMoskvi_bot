from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database import DB
from modules.database.placemark.tag import Tag


class PlacemarkNotFoundError(Exception):
    def __str__(self) -> str:
        return "Placemark not found"


class PlacemarkAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "Placemark already exists"


class IncorrectPlacemarkArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect placemark arguments"


# database container structure
@dataclass
class DbPlacemark:
    id: int
    user_id: int
    datetime: str
    address: str
    latitude: str
    longitude: str
    description: str
    status: str


class PlacemarkDeleter:
    @staticmethod
    def delete(placemark: DbPlacemark):
        DB.delete_one(DB.placemarks_table_name, id=placemark.id)
        DB.delete_one(DB.placemarks_tags_table_name, id=placemark.id)

    @staticmethod
    def delete_tag(placemark_id: int, tag_id: int):
        DB.delete_one(DB.placemarks_tags_table_name, placemark_id=placemark_id, tag_id=tag_id)


class PlacemarkUpdater:
    @staticmethod
    def update_address(placemark: DbPlacemark, address: str):
        DB.update_one(DB.placemarks_table_name, {"id":placemark.id}, {"address": address})

    @staticmethod
    def update_latitude(placemark: DbPlacemark, latitude: str):
        DB.update_one(DB.placemarks_table_name, {"id":placemark.id}, {"latitude": latitude})

    @staticmethod
    def update_longitude(placemark: DbPlacemark, longitude: str):
        DB.update_one(DB.placemarks_table_name, {"id":placemark.id}, {"longitude": longitude})

    @staticmethod
    def update_description(placemark: DbPlacemark, description: str):
        DB.update_one(DB.placemarks_table_name, {"id":placemark.id}, {"description": description})

    @staticmethod
    def reject(tag_id: int):
        DB.update_one(DB.placemarks_table_name, {"id": tag_id}, {"status": "rejected"})

    @staticmethod
    def pending(tag_id: int):
        DB.update_one(DB.placemarks_table_name, {"id": tag_id}, {"status": "pending"})

    @staticmethod
    def approve(tag_id: int):
        DB.update_one(DB.placemarks_table_name, {"id": tag_id}, {"status": "approved"})


class PlacemarkFetcher:
    @staticmethod
    def fetch_all() -> List[DbPlacemark]:
        return PlacemarkFetcher.constructor(DB.fetch_many(DB.placemarks_table_name))

    @staticmethod
    def fetch_approved() -> List[DbPlacemark]:
        return PlacemarkFetcher.constructor(DB.fetch_many(DB.placemarks_table_name, status="approved"))

    @staticmethod
    def fetch_pending() -> List[DbPlacemark]:
        return PlacemarkFetcher.constructor(DB.fetch_many(DB.placemarks_table_name, status="pending"))

    @staticmethod
    def fetch_by_user_id(user_id: int):
        return PlacemarkFetcher.constructor(DB.fetch_many(DB.placemarks_table_name, user_id=user_id))

    @staticmethod
    def fetch_tags(placemark_id):
        tags_info = DB.fetch_many(DB.placemarks_tags_table_name, placemark_id=placemark_id)
        if not tags_info:
            return []

        if not isinstance(tags_info, list):
            tags_info = [tags_info]

        return [tag_info["tag_id"] for tag_info in tags_info]

    @staticmethod
    def fetch_by_id(id: int) -> DbPlacemark:
        return PlacemarkFetcher.constructor(DB.fetch_one(DB.placemarks_table_name, id=id))

    @staticmethod
    def fetch_by_coordinates(latitude: str, longitude: str) -> DbPlacemark:
        return PlacemarkFetcher.constructor(
            DB.fetch_one(DB.placemarks_table_name, latitude=latitude, longitude=longitude))

    @staticmethod
    def constructor(info) -> DbPlacemark | List[DbPlacemark] | None:
        if not info:
            return None

        if isinstance(info, list):
            placemarks = [PlacemarkFetcher.constructor(placemark_info) for placemark_info in info]

            if placemarks:
                return placemarks

            return []

        else:
            return DbPlacemark(**dict(info))


class PlacemarkInserter:
    @staticmethod
    def insert(user_id, datetime: str, address: str, latitude: str, longitude: str, description: str, status: str):
        return DB.insert_one(DB.placemarks_table_name,
                             user_id=user_id, datetime=datetime,
                             address=address,
                             latitude=latitude, longitude=longitude,
                             description=description, status=status)

    @staticmethod
    def insert_tag(placemark_id: int, tag_id: int):
        return DB.insert_one(DB.placemarks_tags_table_name, placemark_id=placemark_id, tag_id=tag_id)


class Placemark:
    _placemark: DbPlacemark

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._placemark = PlacemarkFetcher.fetch_by_id(kwargs.get("id"))

        elif "latitude" in kwargs_keys and "longitude" in kwargs_keys:
            self._placemark = PlacemarkFetcher.fetch_by_coordinates(kwargs.get("latitude"), kwargs.get("longitude"))

        elif kwargs_keys == {"db_placemark"}:
            self._placemark = kwargs.get("db_placemark")

        else:
            raise IncorrectPlacemarkArgumentsError()

        if not self._placemark:
            raise PlacemarkNotFoundError

    @property
    def id(self) -> int:
        return self._placemark.id

    @property
    def user_id(self) -> int:
        return self._placemark.user_id

    @property
    def datetime(self) -> str:
        return self._placemark.datetime

    @property
    def address(self) -> str:
        return self._placemark.address

    @address.setter
    def address(self, address: str) -> None:
        PlacemarkUpdater.update_address(self._placemark, address)
        self.pending()

    @property
    def latitude(self) -> str:
        return self._placemark.latitude

    @latitude.setter
    def latitude(self, latitude: str) -> None:
        PlacemarkUpdater.update_latitude(self._placemark, latitude)
        self.pending()

    @property
    def longitude(self):
        return self._placemark.longitude

    @longitude.setter
    def longitude(self, longitude: str) -> None:
        PlacemarkUpdater.update_longitude(self._placemark, longitude)
        self.pending()

    @property
    def coordinates(self):
        return self._placemark.latitude, self._placemark.longitude

    @property
    def description(self) -> str:
        return self._placemark.description

    @description.setter
    def description(self, description: str):
        PlacemarkUpdater.update_description(self._placemark, description)
        self.pending()

    def approve(self):
        PlacemarkUpdater.approve(self.id)

    def pending(self):
        PlacemarkUpdater.pending(self.id)

    def reject(self):
        PlacemarkUpdater.reject(self.id)

    @property
    def tags(self) -> List[Tag]:
        tags_id = PlacemarkFetcher.fetch_tags(self.id)
        if not tags_id:
            return []

        return [Tag(id=tag_id) for tag_id in tags_id]

    def insert_tag(self, tag: Tag):
        PlacemarkInserter.insert_tag(self.id, tag.id)

    def delete_tag(self, tag: Tag) -> None:
        PlacemarkDeleter.delete_tag(self.id, tag.id)

    @staticmethod
    def all() -> Placemark | List[Placemark]:
        placemarks = PlacemarkFetcher.fetch_all()

        if placemarks:
            return [Placemark(db_placemark=info) for info in placemarks]

        return []

    @staticmethod
    def approved():
        placemarks = PlacemarkFetcher.fetch_approved()

        if placemarks:
            return [Placemark(db_placemark=info) for info in placemarks]

        return []

    @staticmethod
    def get_pending():
        placemarks = PlacemarkFetcher.fetch_pending()

        if placemarks:
            return [Placemark(db_placemark=info) for info in placemarks]

        return []

    @staticmethod
    def user_placemarks(user_id: int) -> List[DbPlacemark]:
        return PlacemarkFetcher.fetch_by_user_id(user_id=user_id)

    @staticmethod
    def insert(user_id, datetime: str, address, latitude: str, longitude: str, description: str,
               status="pending") -> Placemark:
        placemark_id = PlacemarkInserter.insert(user_id, datetime, address, latitude, longitude, description, status)

        return Placemark(id=placemark_id)

    def delete(self):
        PlacemarkDeleter.delete(self._placemark)


if __name__ == "__main__":
    pass

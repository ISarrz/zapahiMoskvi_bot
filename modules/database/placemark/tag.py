from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database.database.database import DB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.database.placemark.category import Category


class TagNotFoundError(Exception):
    def __str__(self) -> str:
        return "Tag not found"


class TagAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "Tag already exists"


class IncorrectTagArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect tag arguments"


# database container structure
@dataclass
class DbTag:
    id: int
    name: str
    user_id: int
    status: str


class TagDeleter:
    @staticmethod
    def delete(tag: DbTag):
        DB.delete_one(DB.tags_table_name, id=tag.id)
        DB.delete_one(DB.tags_categories_table_name, tag_id=tag.id)
        DB.delete_one(DB.placemarks_tags_table_name, tag_id=tag.id)

    @staticmethod
    def delete_category(tag_id: int, category_id: int):
        DB.delete_one(DB.tags_categories_table_name, tag_id=tag_id, category_id=category_id)


class TagUpdater:
    @staticmethod
    def update_name(tag: DbTag, name: str):
        DB.update_one(DB.tags_table_name, tag.__dict__, {"name": name})

    @staticmethod
    def approve(tag_id: int):
        DB.update_one(DB.tags_table_name, {"id": tag_id}, {"status": "approved"})

    @staticmethod
    def reject(tag_id: int):
        DB.update_one(DB.tags_table_name, {"id": tag_id}, {"status": "rejected"})


class TagFetcher:
    @staticmethod
    def fetch_all() -> List[DbTag]:
        return TagFetcher.constructor(DB.fetch_many(DB.tags_table_name))
    @staticmethod
    def fetch_placemarks_by_tag(tag_id:int) -> List[int]:
        info = DB.fetch_many(DB.placemarks_tags_table_name, tag_id=tag_id)
        if not info:
            return []
        if not isinstance(info, list):
            info = [info]

        placemarks_ids=[row["placemark_id"] for row in info]
        return placemarks_ids

    @staticmethod
    def fetch_category_id(tag_id: int) -> int:
        info = DB.fetch_one(DB.tags_categories_table_name, tag_id=tag_id)
        if not info:
            return -1

        return info["category_id"]

    @staticmethod
    def fetch_by_status(status: str) -> List[DbTag]:
        return TagFetcher.constructor(DB.fetch_many(DB.tags_table_name, status=status))

    @staticmethod
    def fetch_approved_and_user(user_id) -> List[DbTag]:
        return TagFetcher.constructor(DB.fetch_many_or(DB.tags_table_name, [
            {"user_id": user_id},
            {"status": "approved"}
        ]))

    @staticmethod
    def fetch_by_id(id: int) -> DbTag:
        return TagFetcher.constructor(DB.fetch_one(DB.tags_table_name, id=id))

    @staticmethod
    def fetch_by_name(name: str) -> DbTag:
        return TagFetcher.constructor(DB.fetch_one(DB.tags_table_name, name=name))

    @staticmethod
    def constructor(info) -> DbTag | List[DbTag] | None:
        if not info:
            return None

        if isinstance(info, list):
            tags = [TagFetcher.constructor(tag_info) for tag_info in info]

            if tags:
                return tags

            return []

        else:
            return DbTag(**dict(info))


class TagInserter:
    @staticmethod
    def insert(name: str, user_id: int, status: str):
        return DB.insert_one(DB.tags_table_name, name=name, user_id=user_id, status=status)

    @staticmethod
    def insert_category(tag_id: int, category_id: int):
        return DB.insert_one(DB.tags_categories_table_name, tag_id=tag_id, category_id=category_id)


class Tag:
    _tag: DbTag

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._tag = TagFetcher.fetch_by_id(kwargs.get("id"))

        elif "name" in kwargs_keys:
            self._tag = TagFetcher.fetch_by_name(kwargs.get("name"))

        elif kwargs_keys == {"db_tag"}:
            self._tag = kwargs.get("db_tag")

        else:
            raise IncorrectTagArgumentsError()

        if not self._tag:
            raise TagNotFoundError

    @property
    def id(self) -> int:
        return self._tag.id

    @property
    def name(self) -> str:
        return self._tag.name

    @property
    def category_id(self) -> int:
        return TagFetcher.fetch_category_id(self.id)

    @property
    def user_id(self) -> int:
        return self._tag.user_id

    @property
    def placemarks_count(self)->int:
        return len(TagFetcher.fetch_placemarks_by_tag(self.id))

    @property
    def status(self) -> str:
        return self._tag.status

    def approve(self):
        TagUpdater.approve(self.id)

    def reject(self):
        TagUpdater.reject(self.id)

    @name.setter
    def name(self, name: str) -> None:
        TagUpdater.update_name(self._tag, name)

    @staticmethod
    def all() -> Tag | List[Tag]:
        tags = TagFetcher.fetch_all()

        if tags:
            return [Tag(db_tag=info) for info in tags]

        return []

    @staticmethod
    def approved():
        tags = TagFetcher.fetch_by_status(status="approved")

        if tags:
            return [Tag(db_tag=info) for info in tags]

        return []

    @staticmethod
    def pending():
        tags = TagFetcher.fetch_by_status(status="pending")

        if tags:
            return [Tag(db_tag=info) for info in tags]

        return []

    @staticmethod
    def approved_and_user(user_id: int):
        tags = TagFetcher.fetch_approved_and_user(user_id)

        if tags:
            return [Tag(db_tag=info) for info in tags]

        return []

    def insert_category(self, category: Category):
        TagInserter.insert_category(self.id, category.id)

    def delete_category(self, category: Category):
        TagDeleter.delete_category(self.id, category.id)

    @staticmethod
    def insert(name: str, user_id: int, status="pending") -> Tag:
        try:
            Tag(name=name)

            raise TagAlreadyExistsError

        except TagNotFoundError:
            tag_id = TagInserter.insert(name=name, user_id=user_id, status=status)

            return Tag(id=tag_id)

    @staticmethod
    def safe_insert(name: str, user_id: int, status="pending") -> Tag | None:
        try:
            Tag(name=name)

        except TagNotFoundError:
            tag_id = TagInserter.insert(name=name, user_id=user_id, status=status)

            return Tag(id=tag_id)

    def delete(self):
        TagDeleter.delete(self._tag)


if __name__ == "__main__":
    pass

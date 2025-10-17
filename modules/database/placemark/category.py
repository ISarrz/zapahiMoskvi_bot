from __future__ import annotations

from typing import List
from dataclasses import dataclass
from modules.database import DB
from modules.database.placemark.tag import Tag


class CategoryNotFoundError(Exception):
    def __str__(self) -> str:
        return "Category not found"


class CategoryAlreadyExistsError(Exception):
    def __str__(self) -> str:
        return "Category already exists"


class IncorrectCategoryArgumentsError(Exception):
    def __str__(self) -> str:
        return "Incorrect category arguments"


# database container structure
@dataclass
class DbCategory:
    id: int
    name: str
    user_id: int
    status: str


class CategoryDeleter:
    @staticmethod
    def delete(category: DbCategory):
        DB.delete_one(DB.categories_table_name, id=category.id)
        info = DB.fetch_many(DB.tags_categories_table_name, category_id=category.id)
        if not info:
            return

        if not isinstance(info, list):
            info = [info]

        for row in info:
            DB.delete_one(DB.tags_categories_table_name, id=row["id"])
            DB.delete_one(DB.tags_table_name, id=row["tag_id"])


class CategoryUpdater:
    @staticmethod
    def update_name(category_id: int, name: str):
        DB.update_one(DB.categories_table_name, {"id": category_id}, {"name": name})

    @staticmethod
    def approve(category_id: int):
        DB.update_one(DB.categories_table_name, {"id": category_id}, {"status": "approved"})

    @staticmethod
    def reject(tag_id: int):
        DB.update_one(DB.categories_table_name, {"id": tag_id}, {"status": "rejected"})


class CategoryFetcher:
    @staticmethod
    def fetch_all() -> List[DbCategory]:
        return CategoryFetcher.constructor(DB.fetch_many(DB.categories_table_name))

    @staticmethod
    def fetch_approved() -> List[DbCategory]:
        return CategoryFetcher.constructor(DB.fetch_many(DB.categories_table_name, status="approved"))

    @staticmethod
    def fetch_by_id(id: int) -> DbCategory:
        return CategoryFetcher.constructor(DB.fetch_one(DB.categories_table_name, id=id))

    @staticmethod
    def fetch_approved_and_user(user_id: int) -> List[DbCategory]:
        return CategoryFetcher.constructor(DB.fetch_many_or(DB.categories_table_name, [
            {"user_id": user_id},
            {"status": "approved"}
        ]))

    @staticmethod
    def fetch_tags(category_id: int) -> List[int]:
        tags_info = DB.fetch_many(DB.tags_categories_table_name, category_id=category_id)
        if not tags_info:
            return []

        if not isinstance(tags_info, list):
            tags_info = [tags_info]

        tags_id = [tag_info["tag_id"] for tag_info in tags_info]

        return tags_id

    @staticmethod
    def fetch_by_name(name: str) -> DbCategory:
        return CategoryFetcher.constructor(DB.fetch_one(DB.categories_table_name, name=name))

    @staticmethod
    def fetch_by_tag_id(tag_id: int):
        categories_id = [info["category_id"] for info in
                         DB.fetch_many(DB.tags_categories_table_name, tag_id=tag_id)]
        if categories_id:
            return [CategoryFetcher.fetch_by_id(category_id) for category_id in categories_id]

        return []

    @staticmethod
    def constructor(info) -> DbCategory | List[DbCategory] | None:
        if not info:
            return None

        if isinstance(info, list):
            categories = [CategoryFetcher.constructor(category_info) for category_info in info]

            if categories:
                return categories

            return []

        else:
            return DbCategory(**dict(info))


class CategoriesInserter:
    @staticmethod
    def insert(name: str, user_id: int, status: str):
        return DB.insert_one(DB.categories_table_name, name=name, user_id=user_id, status=status)


class Category:
    _category: DbCategory

    def __init__(self, *args, **kwargs):
        kwargs_keys = set(kwargs.keys())

        if kwargs_keys == {"id"}:
            self._category = CategoryFetcher.fetch_by_id(kwargs.get("id"))

        elif kwargs_keys == {"name"}:
            self._category = CategoryFetcher.fetch_by_name(kwargs.get("name"))

        elif kwargs_keys == {"db_category"}:
            self._category = kwargs.get("db_category")

        else:
            raise IncorrectCategoryArgumentsError()

        if not self._category:
            raise CategoryNotFoundError

    @property
    def id(self) -> int:
        return self._category.id

    @property
    def tags(self):
        tags_id = CategoryFetcher.fetch_tags(self.id)
        if not tags_id:
            return []

        return [Tag(id=tag_id) for tag_id in tags_id]

    @property
    def name(self) -> str:
        return self._category.name

    @name.setter
    def name(self, name: str) -> None:
        CategoryUpdater.update_name(self.id, name)

    @property
    def status(self) -> str:
        return self._category.status

    @property
    def user_id(self) -> int:
        return self._category.user_id

    def reject(self):
        CategoryUpdater.reject(self.id)

    @staticmethod
    def all() -> Category | List[Category]:
        categories = CategoryFetcher.fetch_all()

        if categories:
            return [Category(db_category=info) for info in categories]

        return []

    @staticmethod
    def approved():
        categories = CategoryFetcher.fetch_approved()

        if categories:
            return [Category(db_category=info) for info in categories]

        return []

    @staticmethod
    def approved_and_user(user_id: int):
        categories = CategoryFetcher.fetch_approved_and_user(user_id)

        if categories:
            return [Category(db_category=info) for info in categories]

        return []

    @staticmethod
    def by_tag_id(tag_id: int):
        categories = CategoryFetcher.fetch_by_tag_id(tag_id)
        if categories:
            return [Category(db_category=category) for category in categories]

        return []

    @staticmethod
    def insert(name: str, user_id: int, status="pending") -> Category | None:
        try:
            Category(name=name)

            raise CategoryAlreadyExistsError

        except CategoryNotFoundError:
            category_id = CategoriesInserter.insert(name, user_id, status)

            return Category(id=category_id)

    @staticmethod
    def safe_insert(name: str, user_id: int, status="pending") -> Category | None:
        try:
            Category(name=name)


        except CategoryNotFoundError:
            category_id = CategoriesInserter.insert(name, user_id, status)

            return Category(id=category_id)

    def approve(self):
        CategoryUpdater.approve(self.id)

    def delete(self):
        CategoryDeleter.delete(self._category)


if __name__ == "__main__":
    pass

import sqlite3

from modules.config.paths import database_path, database_dump_path
import re
import os
from typing import List


class DB:
    users_table_name = "users"
    users_notifications_table_name = "users_notifications"
    placemarks_table_name = "placemarks"
    categories_table_name = "categories"
    tags_table_name = "tags"
    tags_categories_table_name = "tags_categories"
    placemarks_tags_table_name = "placemarks_tags"

    logs_table_name = "logs"

    @staticmethod
    def save_backup():
        if not os.path.exists(database_path):
            raise FileNotFoundError(f"Source database not found")

        with sqlite3.connect(database_path) as src_conn:
            with sqlite3.connect(database_dump_path) as dest_conn:
                src_conn.backup(dest_conn, pages=0, progress=None)

    @staticmethod
    def load_backup():
        if not os.path.exists(database_dump_path):
            raise FileNotFoundError(f"Source dump database not found")

        if os.path.exists(database_path):
            os.remove(database_path)

        with sqlite3.connect(database_dump_path) as src_conn:
            with sqlite3.connect(database_path) as dest_conn:
                src_conn.backup(dest_conn, pages=0, progress=None)

    @staticmethod
    def fetch_one(table_name: str, **kwargs):
        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
                SELECT * FROM {table_name} {where_request}
                """, tuple(kwargs.values()))

            response = cur.fetchone()

        return response

    @staticmethod
    def fetch_many(table_name: str, **kwargs):
        # не доделано, в значения должно подставляться list[tuple]

        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            SELECT * FROM {table_name} {where_request}
            """, tuple(kwargs.values()))

            response = cur.fetchall()

        return response

    @staticmethod
    def delete_one(table_name: str, **kwargs):
        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()
            cur.execute(f"""
            DELETE FROM {table_name} {where_request}
            """, tuple(kwargs.values()))

    @staticmethod
    def delete_many(table_name: str, **kwargs):
        # не доделано, в значения должно подставляться list[tuple]

        where_request = DB.create_where_request(**kwargs)

        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()
            cur.executemany(f"""
            DELETE FROM {table_name} {where_request}
            """, tuple(kwargs.values()))

    @staticmethod
    def update_one(table_name: str, row_info: dict, new_values: dict):
        where_request = DB.create_where_request(**row_info)
        set_request = DB.create_set_request(**new_values)
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            UPDATE {table_name} {set_request} {where_request}
            """, tuple(new_values.values()) + tuple(row_info.values()))

    @staticmethod
    def update_many(table_name: str, row_info: dict, new_values: dict):
        # не доделано, в значения должно подставляться list[tuple]

        where_request = DB.create_where_request(**row_info)
        set_request = DB.create_set_request(**new_values)
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.executemany(f"""
            UPDATE {table_name} {set_request} {where_request}
            """, tuple(new_values.values()) + tuple(row_info.values()))

    @staticmethod
    def find_pattern(text, patterns):
        for pattern in patterns:
            if re.fullmatch(pattern[1], text, re.IGNORECASE):
                return pattern[0]

        return None

    @staticmethod
    def insert_one(table_name: str, **kwargs):
        insert_request = DB.create_insert_request(**kwargs)
        new_id = None
        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f"""
            INSERT INTO {table_name} {insert_request}
            """, tuple(kwargs.values()))

            new_id = cur.lastrowid

        return new_id

    @staticmethod
    def create_where_request(**kwargs):
        return "WHERE " + " AND ".join(f"{arg} = ?" for arg in kwargs.keys()) if kwargs else ""

    @staticmethod
    def fetch_one_or(table_name:str, conditions: List[dict]):
        where_request = DB.create_where_or_request(conditions)

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            values = []
            for condition in conditions:
                values += list(condition.values())

            cur.execute(f"""
                        SELECT * FROM {table_name} {where_request}
                        """, tuple(values))

            response = cur.fetchone()

        return response
    @staticmethod
    def fetch_many_or(table_name:str, conditions: List[dict]):
        where_request = DB.create_where_or_request(conditions)

        with sqlite3.connect(database_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            values = []
            for condition in conditions:
                values += list(condition.values())

            cur.execute(f"""
                        SELECT * FROM {table_name} {where_request}
                        """, tuple(values))

            response = cur.fetchall()

        return response

    @staticmethod
    def create_where_or_request(conditions: List[dict]):
        text_conditions = []
        for condition in conditions:
            text_conditions.append("(" + " AND ".join(f"{arg} = ?" for arg in condition.keys()) + ")")
        res = "WHERE " + " OR ".join(text_conditions) if text_conditions else ""

        return res

    @staticmethod
    def create_set_request(**kwargs):
        return "SET " + ", ".join(f"{arg} = ?" for arg in kwargs.keys()) if kwargs else ""

    @staticmethod
    def create_insert_request(**kwargs):
        if not kwargs:
            return ""

        request = "(" + ", ".join(f"{arg}" for arg in kwargs.keys()) + ") "
        request += "VALUES (" + ", ".join(["?" for _ in range(len(kwargs))]) + ")"

        return request

    @staticmethod
    def initialize():
        DB._create_users_table()
        DB._create_users_notifications()
        DB._create_logs_table()
        DB._create_categories_table()
        DB._create_tags_table()
        DB._create_tags_categories_table()
        DB._create_placemarks_tags_table()
        DB._create_placemarks_table()

        print("Database initialized.")

    @staticmethod
    def _create_users_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users
                        (
                            id          INTEGER PRIMARY KEY AUTOINCREMENT,
                            telegram_id INTEGER,
                            role TEXT
                        )""")

    @staticmethod
    def _create_logs_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS logs
                        (
                            id    INTEGER PRIMARY KEY AUTOINCREMENT,
                            value TEXT
                        )""")

    @staticmethod
    def _create_placemarks_table():
        with (sqlite3.connect(database_path) as conn):
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS placemarks
                        (
                            id          INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id     INTEGER REFERENCES users,
                            datetime    TEXT,
                            address     TEXT,
                            latitude    TEXT,
                            longitude   TEXT,
                            description TEXT,
                            status      TEXT
                        )""")

    @staticmethod
    def _create_users_notifications():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users_notifications
                        (
                            id      INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER REFERENCES users,
                            weekday INTEGER,
                            time    TEXT
                        )""")

    @staticmethod
    def _create_categories_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS categories
                        (
                            id      INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER REFERENCES users,
                            name    TEXT,
                            status  TEXT
                        )""")

    @staticmethod
    def _create_tags_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS tags
                        (
                            id   INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER REFERENCES users,
                            name TEXT,
                            status  TEXT

                        )""")

    @staticmethod
    def _create_tags_categories_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS tags_categories
                        (
                            id          INTEGER PRIMARY KEY AUTOINCREMENT,
                            tag_id      INTEGER REFERENCES tags,
                            category_id INTEGER REFERENCES categories

                        )""")

    @staticmethod
    def _create_placemarks_tags_table():
        with sqlite3.connect(database_path) as conn:
            cur = conn.cursor()

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS placemarks_tags
                        (
                            id           INTEGER PRIMARY KEY AUTOINCREMENT,
                            placemark_id INTEGER REFERENCES placemarks,
                            tag_id       INTEGER REFERENCES tags

                        )""")


if __name__ == "__main__":
    # DB.save_backup()
    # DB.load_backup()


    pass

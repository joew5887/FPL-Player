import sqlite3
from itertools import chain
from requests import get
from json import loads
from typing import Union
import pandas as pd


class Database:
    TABLE_NAMES_QUERY = "SELECT name FROM sqlite_master WHERE type = 'table'"

    def __init__(self, path: str):
        self.__path = path
        self.__sql = sqlite3.connect(self.__path)
        self.__cursor = self.__sql.cursor()

        self.__set_table_names()
        self.__set_columns()

    def __del__(self) -> None:
        self.__cursor.close()
        self.__sql.close()

    @property
    def table_names(self) -> tuple:
        return self.__table_names

    def __set_table_names(self) -> None:
        table_names = self.__cursor.execute(Database.TABLE_NAMES_QUERY)
        table_names = tuple(table_names)
        table_list_1d = chain.from_iterable(table_names)

        self.__table_names = tuple(table_list_1d)

    def columns(self, table_name: str) -> Union[tuple, KeyError]:
        if table_name not in self.__columns:
            raise KeyError(f"'{table_name}' not in '{self.table_names}'")

        return self.__columns.get(table_name)

    def __set_columns(self) -> None:
        table_to_columns = {}

        for name in self.table_names:
            self.search(f"SELECT * FROM {name}")
            columns = self.__info()
            table_to_columns[name] = columns

        self.__columns = table_to_columns

    def search(self, query: str) -> tuple:
        return tuple(self.__cursor.execute(query))

    # Should check if update was successful
    def update(self, query: str) -> None:
        self.__cursor.execute(query)

    def save_changes(self) -> None:
        self.__sql.commit()

    def __info(self) -> list[str]:
        return [col[0] for col in self.__cursor.description]


class API:
    def __init__(self, link: str):
        self.__link = link
        self.__set_data()

    @property
    def data(self) -> dict:
        return self.__data

    def __set_data(self) -> None:
        response = get(self.__link)
        utf8 = response.text.encode("utf8")
        json_data = utf8.decode("unicode_escape")
        self.__data = loads(json_data)
        print("foo")

    @property
    def df(self) -> pd.DataFrame:
        return pd.json_normalize(self.data)

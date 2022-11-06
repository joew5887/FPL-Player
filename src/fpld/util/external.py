from typing import Any
import requests
from json import loads
import pandas as pd


class API:
    def __init__(self, url_link: str):
        self.__url_link = url_link
        self.__set_data()

    def __str__(self) -> str:
        return str(self.data)

    @property
    def data(self) -> Any:
        return self.__data

    def __set_data(self) -> None:
        response = requests.get(self.__url_link)
        utf8 = response.text.encode("utf8")
        json_data = utf8.decode("unicode_escape")
        self.__data = loads(json_data)

    @property
    def df(self) -> pd.DataFrame:
        return pd.json_normalize(self.data)

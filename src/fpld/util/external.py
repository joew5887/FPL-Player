from requests import get
from json import loads
import pandas as pd


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

    @property
    def df(self) -> pd.DataFrame:
        return pd.json_normalize(self.data)

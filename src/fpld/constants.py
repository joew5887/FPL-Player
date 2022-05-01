from datetime import datetime

__STR_TO_DATETIME = "%Y-%m-%dT%H:%M:%SZ"
API_URL = "https://fantasy.premierleague.com/api/"


def str_to_datetime(str_date: str, format: str = __STR_TO_DATETIME) -> datetime:
    return datetime.strptime(str_date, format)

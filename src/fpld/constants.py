from datetime import datetime

__STR_TO_DATETIME = "%Y-%m-%dT%H:%M:%SZ"
__API_URL_STEM = "https://fantasy.premierleague.com/api/"
URLS = {
    "API": __API_URL_STEM,
    "BOOTSTRAP-STATIC": __API_URL_STEM + "bootstrap-static/",
    "ELEMENT-SUMMARY": __API_URL_STEM + "element-summary/{}/",
    "FIXTURES": __API_URL_STEM + "fixtures/"}


def str_to_datetime(str_date: str, format: str = __STR_TO_DATETIME) -> datetime:
    return datetime.strptime(str_date, format)

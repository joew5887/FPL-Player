from datetime import datetime

__STR_TO_DATETIME = "%Y-%m-%dT%H:%M:%SZ"  # Format of dates in FPL API
API_URL_STEM = "https://fantasy.premierleague.com/api/"
URLS = {
    "API": API_URL_STEM,
    "BOOTSTRAP-STATIC": API_URL_STEM + "bootstrap-static/",
    "ELEMENT-SUMMARY": API_URL_STEM + "element-summary/{}/",
    "FIXTURES": API_URL_STEM + "fixtures/"
}


def date_to_string(date_: datetime) -> str:
    """Converts the date from a datetime object to a string.

    E.g. '10-02-2000' becomes 'Thu 10 February 2000' 

    Parameters
    ----------
    date_ : datetime
        Date to represent in string form.

    Returns
    -------
    str
        Date in string form.
    """
    return date_.strftime("%a %d %B %Y")


def time_to_string(date_: datetime) -> str:
    """Converts the time from a datetime object to a string.

    Parameters
    ----------
    date_ : datetime
        Time to represent in string form.

    Returns
    -------
    str
        Time in string form, 24hr clock 'HH:MM'.
    """
    return date_.strftime("%H:%M")


def datetime_to_string(date_: datetime) -> str:
    """Converts whole datetime object to string.

    '10-02-2000 13:20' becomes '13:20 - Thu 10 February 2000'

    Parameters
    ----------
    date_ : datetime
        Date and time to represent in string form.

    Returns
    -------
    str
        Datetime represented in string form.
    """
    return time_to_string(date_) + " - " + date_to_string(date_)


def string_to_datetime(str_date: str, format: str = __STR_TO_DATETIME) -> datetime:
    """Converts string into datetime object with a specified format.

    Parameters
    ----------
    str_date : str
        String date to convert to datetime object.
    format : str, optional
        Format `str_date` is in, by default `__STR_TO_DATETIME`

    Returns
    -------
    datetime
        Datetime object from `str_date`.
    """
    return datetime.strptime(str_date, format)

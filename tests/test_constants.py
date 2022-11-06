import pytest
import fpld
from datetime import datetime


@pytest.mark.parametrize("input_date,expected", [(datetime(2000, 2, 10), "Thu 10 February 2000")])
def test_date_to_string(input_date: datetime, expected: str) -> None:
    assert fpld.constants.date_to_string(input_date) == expected


@pytest.mark.parametrize("input_date,expected", [(datetime(2000, 2, 10, 9, 30, 00), "09:30")])
def test_time_to_string(input_date: datetime, expected: str) -> None:
    assert fpld.constants.time_to_string(input_date) == expected


@pytest.mark.parametrize("input_date,expected", [(datetime(2000, 2, 10, 9, 30, 00), "09:30 - Thu 10 February 2000")])
def test_datetime_to_string(input_date: datetime, expected: str) -> None:
    assert fpld.constants.datetime_to_string(input_date) == expected


@pytest.mark.parametrize("input_str,expected", [("2000-02-10T09:30:00Z", datetime(2000, 2, 10, 9, 30, 00))])
def test_string_to_datetime(input_str: str, expected: datetime) -> None:
    assert fpld.constants.string_to_datetime(input_str) == expected


@pytest.mark.parametrize("input_value,expected", [(5.8888, 5.889), (3.1415654, 3.142)])
def test_round_value(input_value: float, expected: float) -> None:
    assert fpld.constants.round_value(input_value) == expected

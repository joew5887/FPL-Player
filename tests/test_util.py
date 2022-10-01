import pytest
from fpld import util
import fpld
import pandas as pd
import requests


class TestPercent:
    @pytest.mark.parametrize("numerator, denominator, expected", [(10, 0, 0.0), (5, 10, 50.0), (0, 10, 0.0)])
    def test_percent(self, numerator: int, denominator: int, expected: float) -> None:
        assert util.to_percent(numerator, denominator) == expected


class TestAPI:
    def test_expected_api_call(self) -> None:
        url = fpld.constants.URLS["BOOTSTRAP-STATIC"]
        api = util.API(url)

        assert isinstance(api.data, dict)
        assert isinstance(api.df, pd.DataFrame)
        assert str(api.data) == str(api)

    def test_invalid_url(self) -> None:
        url = ""

        with pytest.raises(requests.exceptions.MissingSchema):
            util.API(url)

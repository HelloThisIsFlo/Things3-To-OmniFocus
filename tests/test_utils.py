from src.utils import convert_bin_date
from datetime import date


def test_convert_bin_date():
    # See: https://www.reddit.com/r/thingsapp/comments/12ivjn6/comment/jfxg3er
    assert convert_bin_date(132598144) == date(2023, 4, 19)
    assert convert_bin_date(132601088) == date(2023, 5, 10)

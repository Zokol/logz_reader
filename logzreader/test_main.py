import os
from unittest import TestCase, mock
from main import LogzSearch


class TestLogzSearch(TestCase):
    @mock.patch.dict(
        os.environ, {
            "URL": "https://api-eu.logz.io/v1/search",
            "TOKEN": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
    )
    def setUp(self) -> None:
        start_time = "2022-07-14T00:00:00.00+00:00"
        end_time = "2022-07-15T00:00:00.00+00:00"
        self.search = LogzSearch(start=start_time, end=end_time)

    def test_convert_logz_timestamp_to_unix(self):
        logz_time = "2022-09-07T06:00:59.000000+0000"
        unix_time = 1662530459
        self.assertEqual(unix_time, self.search.convert_logz_timestamp_to_unix(logz_time))

    def test_convert_unix_to_logz_timestamp(self):
        logz_time = "2022-09-07T06:00:59.000000+0000"
        unix_time = 1662530459
        self.assertEqual(logz_time, self.search.convert_unix_to_logz_timestamp(unix_time))

    def test_calc_difference_days(self):
        start_time = "2022-07-14T00:00:00.00+00:00"
        end_time = "2022-07-15T00:00:00.00+00:00"
        difference = 1
        self.assertEqual(difference, self.search.day_difference(start_time, end_time))

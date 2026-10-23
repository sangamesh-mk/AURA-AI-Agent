
import unittest
from datetime import datetime
from tools import get_current_datetime


class TestCurrentDateTime(unittest.TestCase):

    def test_returns_nonempty_string(self):
        result = get_current_datetime()
        self.assertIsInstance(result, str)
        self.assertTrue(result.strip())

    def test_contains_current_year(self):
        result = get_current_datetime()
        current_year = str(datetime.now().year)
        self.assertIn(current_year, result)


if __name__ == "__main__":
    unittest.main()

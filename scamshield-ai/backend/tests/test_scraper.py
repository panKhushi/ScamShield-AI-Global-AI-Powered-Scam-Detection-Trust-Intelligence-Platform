import unittest
from unittest.mock import patch

from app.ml import scraper


class ScraperTests(unittest.TestCase):
    def setUp(self):
        self.original_ranks = scraper._tranco_ranks
        scraper._tranco_ranks = None

    def tearDown(self):
        scraper._tranco_ranks = self.original_ranks

    def test_missing_tranco_file_uses_neutral_traffic_score(self):
        with patch.object(scraper.Path, "is_file", return_value=False):
            with self.assertLogs("app.ml.scraper", level="WARNING"):
                self.assertEqual(scraper.get_website_traffic_score("google.com"), 0)


if __name__ == "__main__":
    unittest.main()

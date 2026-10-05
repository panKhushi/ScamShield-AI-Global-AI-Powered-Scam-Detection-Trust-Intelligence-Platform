import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.historical_intelligence import (
    check_history,
    normalize_url,
    record_report,
    record_scan,
)


class HistoricalIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_new_entity_has_no_historical_data(self):
        result = check_history(self.session, "url", "https://new.example/login")

        self.assertFalse(result.found)
        self.assertEqual(result.recency_status, "NO_HISTORICAL_DATA")
        self.assertEqual(result.historical_risk, "UNKNOWN")

    def test_normalized_url_shares_one_record_but_counts_scans_and_reports(self):
        first = "https://www.example.com/login/?b=2&a=1#fragment"
        second = "http://example.com/login?a=1&b=2"

        self.assertEqual(normalize_url(first), normalize_url(second))
        record_scan(self.session, "url", first, "safe", 80, "user-1")
        record_scan(self.session, "url", second, "suspicious", 45, "user-1")
        record_report(self.session, "url", "https://example.com/login", user_id="user-2")

        result = check_history(self.session, "url", "https://example.com/login/")

        self.assertTrue(result.found)
        self.assertEqual(result.scans_last_3_months, 2)
        self.assertEqual(result.reports_last_3_months, 1)
        self.assertEqual(result.historical_risk, "HIGH")
        self.assertEqual(result.matches[0]["match_type"], "exact")

    def test_similar_sms_is_matched_without_merging_entity_types(self):
        record_scan(
            self.session,
            "sms",
            "Congratulations! You won Rs 50,000. Click the link to claim.",
            "dangerous",
            20,
            "user-1",
        )

        result = check_history(
            self.session,
            "sms",
            "Congrats, you won Rs 50,000. Click the link to claim your reward.",
        )
        email_result = check_history(self.session, "email", "Congrats, you won Rs 50,000.")

        self.assertTrue(result.found)
        self.assertEqual(result.matches[0]["match_type"], "similar")
        self.assertFalse(email_result.found)


if __name__ == "__main__":
    unittest.main()

import unittest

from app.services.email_sender_analyzer import analyze_email_sender
from app.services.phone_analyzer import analyze_phone, normalize_phone


class AnalysisHelperTests(unittest.TestCase):
    def test_phone_normalization_and_scam_context(self):
        self.assertEqual(normalize_phone("+91 (987) 654-3210"), "+919876543210")
        factors = analyze_phone("Call +91 9876543210 to verify your OTP")
        self.assertEqual(factors[1].status, "bad")

    def test_brand_impersonation_from_free_email_provider_is_bad(self):
        factors = analyze_email_sender("From: Microsoft Security <microsoft.alert@gmail.com>")
        self.assertEqual(factors[0].status, "bad")

    def test_business_sender_domain_is_detected(self):
        factors = analyze_email_sender("From: alerts@example.org")
        self.assertEqual(factors[0].status, "good")
        self.assertIn("example.org", factors[0].detail)


if __name__ == "__main__":
    unittest.main()
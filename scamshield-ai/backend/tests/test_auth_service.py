import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.services.auth_service import get_optional_current_user


class AuthServiceTests(unittest.TestCase):
    def test_missing_supabase_url_returns_service_unavailable(self):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

        with patch("app.services.auth_service.JWKS_URL", None), patch(
            "app.services.auth_service.jwt.get_unverified_header",
            return_value={"alg": "ES256"},
        ):
            with self.assertRaises(HTTPException) as raised:
                get_optional_current_user(credentials)

        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("SUPABASE_URL", raised.exception.detail)


if __name__ == "__main__":
    unittest.main()

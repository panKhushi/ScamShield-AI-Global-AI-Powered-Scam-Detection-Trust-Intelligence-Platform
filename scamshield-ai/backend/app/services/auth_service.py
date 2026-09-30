import logging
import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer(auto_error=False)

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_URL")
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

_jwks_cache = None
logger = logging.getLogger(__name__)

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        response = requests.get(JWKS_URL, timeout=5)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def get_optional_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict | None:
    if credentials is None:
        return None

    token = credentials.credentials
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        jwks = get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if key is None:
            logger.warning("No matching Supabase JWKS key found for token kid")
            return None

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
        )
        return payload

    except requests.RequestException as e:
        logger.warning("Unable to fetch Supabase JWKS: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable",
        ) from e
    except JWTError as e:
        logger.info("Supabase token validation failed: %s", e)
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    user = get_optional_current_user(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
    return user

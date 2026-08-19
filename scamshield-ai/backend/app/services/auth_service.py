import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer(auto_error=False)

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_URL")
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

_jwks_cache = None

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        print(f"DEBUG: Fetching JWKS from {JWKS_URL}")
        response = requests.get(JWKS_URL, timeout=5)
        print(f"DEBUG: JWKS response status: {response.status_code}")
        response.raise_for_status()
        _jwks_cache = response.json()
        print(f"DEBUG: JWKS keys found: {[k['kid'] for k in _jwks_cache['keys']]}")
    return _jwks_cache


def get_optional_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict | None:
    if credentials is None:
        return None

    token = credentials.credentials
    print(f"DEBUG: Token received (first 30 chars): {token[:30]}...")

    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        print(f"DEBUG: Token kid: {kid}")

        jwks = get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if key is None:
            print("DEBUG: No matching key found in JWKS!")
            return None

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
        )
        return payload

    except JWTError as e:
        print(f"DEBUG: JWTError: {str(e)}")
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict:
    user = get_optional_current_user(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
    return user

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
import httpx

security = HTTPBearer()

CLERK_ISSUER = os.getenv("CLERK_ISSUER")
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE")
CLERK_JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"

_jwks_cache = None


async def get_jwks():
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache

    async with httpx.AsyncClient() as client:
        res = await client.get(CLERK_JWKS_URL)
        res.raise_for_status()
        _jwks_cache = res.json()
        return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        jwks = await get_jwks()
        header = jwt.get_unverified_header(token)

        key = next(
            k for k in jwks["keys"] if k["kid"] == header["kid"]
        )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLERK_AUDIENCE,
            issuer=CLERK_ISSUER,
        )

        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
):
    """Optional authentication - returns demo user if not authenticated"""
    if not credentials:
        return {"user_id": "demo_user", "email": "demo@example.com"}
    
    try:
        token = credentials.credentials
        jwks = await get_jwks()
        header = jwt.get_unverified_header(token)

        key = next(
            k for k in jwks["keys"] if k["kid"] == header["kid"]
        )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=CLERK_AUDIENCE,
            issuer=CLERK_ISSUER,
        )

        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
        }
    except Exception:
        return {"user_id": "demo_user", "email": "demo@example.com"}

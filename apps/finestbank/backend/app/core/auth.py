import time
from typing import Any

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

# Module-level JWKS cache: { kid: { key_data, cached_at } }
_jwks_cache: dict[str, dict[str, Any]] = {}
_CACHE_TTL = 3600  # 1 hour

CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks"


async def _fetch_jwks() -> dict[str, Any]:
    """Fetch JWKS from Clerk and update the module-level cache."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(CLERK_JWKS_URL, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

    now = time.time()
    for key in data.get("keys", []):
        kid = key.get("kid")
        if kid:
            _jwks_cache[kid] = {"key": key, "cached_at": now}

    return _jwks_cache


async def _get_public_key(kid: str) -> dict[str, Any]:
    """Return the public key for a given kid, refreshing cache if stale."""
    now = time.time()
    cached = _jwks_cache.get(kid)

    if cached and (now - cached["cached_at"]) < _CACHE_TTL:
        return cached["key"]

    # Refresh
    await _fetch_jwks()

    cached = _jwks_cache.get(kid)
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Public key not found for token kid",
        )
    return cached["key"]


async def verify_clerk_token(token: str) -> dict[str, Any]:
    """
    Verify a Clerk-issued JWT.
    Returns the decoded payload on success.
    Raises HTTPException(401) on any failure.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing kid",
        )

    public_key = await _get_public_key(kid)

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {exc}",
        )

    return payload

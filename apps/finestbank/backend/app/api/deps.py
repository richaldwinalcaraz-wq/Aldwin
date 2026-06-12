from typing import AsyncGenerator

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_clerk_token
from app.db.session import AsyncSessionLocal

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    payload = await verify_clerk_token(credentials.credentials)
    public_metadata = payload.get("public_metadata") or {}
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email", ""),
        "role": public_metadata.get("role", "viewer"),
        "divisions": public_metadata.get("divisions", []),
    }


async def get_scoped_db(
    current_user: dict = Depends(get_current_user),
) -> AsyncGenerator[AsyncSession, None]:
    """Yields an async DB session with RLS context vars set for the current user."""
    async with AsyncSessionLocal() as session:
        role = current_user.get("role", "viewer")
        divisions = current_user.get("divisions", [])
        division_ids_str = ",".join(str(d) for d in divisions)
        await session.execute(
            text(
                "SELECT set_config('app.role', :role, true), "
                "set_config('app.division_ids', :divs, true)"
            ),
            {"role": role, "divs": division_ids_str},
        )
        yield session

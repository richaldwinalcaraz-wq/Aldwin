from enum import Enum

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user


class Role(str, Enum):
    CFO = "cfo"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Division(str, Enum):
    RETAIL = "retail"
    CORPORATE = "corporate"
    TREASURY = "treasury"
    WEALTH = "wealth"


def require_role(*roles: Role):
    """FastAPI dependency factory. Usage: Depends(require_role(Role.CFO))"""

    async def _check(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "viewer")
        if user_role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' not permitted. Required: {[r.value for r in roles]}",
            )
        return current_user

    return _check


def require_division_access(division: Division):
    """Ensures analyst can only access their assigned divisions. CFO bypasses."""

    async def _check(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role", "viewer")
        if role == Role.CFO.value:
            return current_user  # CFO sees all
        divisions = current_user.get("divisions", [])
        if division.value not in divisions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access to division '{division.value}' not permitted",
            )
        return current_user

    return _check

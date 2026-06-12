import math
import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_scoped_db
from app.core.rbac import Role, require_role
from app.db.models import Division, Loan, PortfolioHolding, Transaction

router = APIRouter(prefix="/analyst", tags=["analyst"])


@router.get("/summary")
async def get_analyst_summary(
    _: dict = Depends(require_role(Role.ANALYST, Role.CFO)),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_scoped_db),
):
    divisions = current_user.get("divisions", [])
    if not divisions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No division assigned to this account",
        )

    division_id = uuid.UUID(str(divisions[0]))

    div_result = await db.execute(
        select(Division).where(Division.id == division_id)
    )
    division = div_result.scalar_one_or_none()
    if division is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Division not found",
        )

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    txn_result = await db.execute(
        select(
            func.count(Transaction.id).label("count"),
            func.coalesce(func.sum(Transaction.amount), 0).label("volume"),
        ).where(Transaction.created_at >= cutoff)
    )
    txn_row = txn_result.one()

    portfolio_result = await db.execute(
        select(func.coalesce(func.sum(PortfolioHolding.market_value), 0))
    )

    loans_result = await db.execute(
        select(func.count(Loan.id)).where(Loan.status == "active")
    )

    return {
        "division": {"name": division.name, "slug": division.slug},
        "transaction_count_30d": int(txn_row.count),
        "transaction_volume_30d": float(txn_row.volume),
        "portfolio_market_value": float(portfolio_result.scalar()),
        "active_loan_count": int(loans_result.scalar()),
    }


@router.get("/transactions")
async def get_analyst_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    type: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    _: dict = Depends(require_role(Role.ANALYST, Role.CFO)),
    db: AsyncSession = Depends(get_scoped_db),
):
    stmt = select(Transaction).order_by(Transaction.created_at.desc())

    if type:
        stmt = stmt.where(Transaction.type == type)
    if category:
        stmt = stmt.where(Transaction.category == category)
    if date_from:
        stmt = stmt.where(
            Transaction.created_at >= datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        )
    if date_to:
        stmt = stmt.where(
            Transaction.created_at < datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=timezone.utc)
        )

    count_result = await db.execute(
        select(func.count()).select_from(stmt.subquery())
    )
    total = count_result.scalar() or 0

    rows_result = await db.execute(
        stmt.offset((page - 1) * page_size).limit(page_size)
    )
    rows = rows_result.scalars().all()

    return {
        "items": [
            {
                "id": str(t.id),
                "type": t.type,
                "category": t.category,
                "amount": float(t.amount),
                "currency": t.currency,
                "description": t.description,
                "reference_id": t.reference_id,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
            }
            for t in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, math.ceil(total / page_size)),
    }


@router.get("/portfolio")
async def get_analyst_portfolio(
    _: dict = Depends(require_role(Role.ANALYST, Role.CFO)),
    db: AsyncSession = Depends(get_scoped_db),
):
    rows_result = await db.execute(
        select(PortfolioHolding).order_by(PortfolioHolding.market_value.desc())
    )
    holdings = rows_result.scalars().all()

    alloc_result = await db.execute(
        select(
            PortfolioHolding.asset_type,
            func.sum(PortfolioHolding.market_value).label("mv"),
        )
        .group_by(PortfolioHolding.asset_type)
        .order_by(func.sum(PortfolioHolding.market_value).desc())
    )
    alloc_rows = alloc_result.all()
    total_mv = sum(float(r.mv) for r in alloc_rows) or 0.0

    return {
        "holdings": [
            {
                "id": str(h.id),
                "asset_name": h.asset_name,
                "asset_type": h.asset_type,
                "ticker": h.ticker,
                "quantity": float(h.quantity),
                "unit_cost": float(h.unit_cost),
                "current_price": float(h.current_price),
                "market_value": float(h.market_value),
                "unrealized_pnl": float(h.unrealized_pnl),
                "weight_pct": float(h.weight_pct),
            }
            for h in holdings
        ],
        "allocation": [
            {
                "asset_type": r.asset_type,
                "market_value": float(r.mv),
                "pct": round(float(r.mv) / total_mv * 100, 1) if total_mv else 0.0,
            }
            for r in alloc_rows
        ],
        "total_market_value": total_mv,
    }

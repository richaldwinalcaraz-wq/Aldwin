from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import case, func, select, text

from app.core.rbac import Role, require_role
from app.db.models import Division, FinancialStatement, Loan
from app.db.session import AsyncSessionLocal

router = APIRouter(tags=["rollup"])


class KpiValue(BaseModel):
    value: float
    change_pct: float


class KpiResponse(BaseModel):
    period: str
    kpis: dict[str, KpiValue]


async def _sum_statement(
    session,
    period_label: str,
    statement_type: str,
    line_item: str,
    division_id=None,
) -> float:
    q = select(func.sum(FinancialStatement.amount)).where(
        FinancialStatement.period_label == period_label,
        FinancialStatement.statement_type == statement_type,
        FinancialStatement.line_item == line_item,
    )
    if division_id is not None:
        q = q.where(FinancialStatement.division_id == division_id)
    result = await session.execute(q)
    return float(result.scalar() or 0.0)


def _change_pct(current: float, prior: float) -> float:
    if prior == 0.0:
        return 0.0
    return round((current - prior) / abs(prior) * 100, 2)


@router.get("/rollup/kpis", response_model=KpiResponse)
async def get_rollup_kpis(
    _: dict = Depends(require_role(Role.CFO)),
    division_slug: Optional[str] = Query(default=None),
    from_period: Optional[str] = Query(default=None),
    to_period: Optional[str] = Query(default=None),
):
    async with AsyncSessionLocal() as session:
        # Resolve division_id if slug provided
        division_id = None
        if division_slug is not None:
            div_result = await session.execute(
                select(Division.id).where(Division.slug == division_slug)
            )
            row = div_result.fetchone()
            if not row:
                return KpiResponse(
                    period="—",
                    kpis={
                        "total_revenue": KpiValue(value=0.0, change_pct=0.0),
                        "net_income": KpiValue(value=0.0, change_pct=0.0),
                        "total_assets": KpiValue(value=0.0, change_pct=0.0),
                        "loan_portfolio": KpiValue(value=0.0, change_pct=0.0),
                    },
                )
            division_id = row[0]

        # Get two most recent period_labels (within optional range)
        periods_q = (
            select(FinancialStatement.period_label)
            .distinct()
            .order_by(FinancialStatement.period_label.desc())
            .limit(2)
        )
        if from_period:
            periods_q = periods_q.where(FinancialStatement.period_label >= from_period)
        if to_period:
            periods_q = periods_q.where(FinancialStatement.period_label <= to_period)

        periods_result = await session.execute(periods_q)
        periods = [row[0] for row in periods_result.fetchall()]

        if not periods:
            return KpiResponse(
                period="—",
                kpis={
                    "total_revenue": KpiValue(value=0.0, change_pct=0.0),
                    "net_income": KpiValue(value=0.0, change_pct=0.0),
                    "total_assets": KpiValue(value=0.0, change_pct=0.0),
                    "loan_portfolio": KpiValue(value=0.0, change_pct=0.0),
                },
            )

        current_period = periods[0]
        prior_period = periods[1] if len(periods) > 1 else None

        cur_revenue = await _sum_statement(session, current_period, "pnl", "Revenue", division_id)
        cur_net_income = await _sum_statement(session, current_period, "pnl", "Net Income", division_id)
        cur_assets = await _sum_statement(session, current_period, "balance_sheet", "Total Assets", division_id)

        if prior_period:
            pri_revenue = await _sum_statement(session, prior_period, "pnl", "Revenue", division_id)
            pri_net_income = await _sum_statement(session, prior_period, "pnl", "Net Income", division_id)
            pri_assets = await _sum_statement(session, prior_period, "balance_sheet", "Total Assets", division_id)
        else:
            pri_revenue = pri_net_income = pri_assets = 0.0

        # Loan portfolio — filter by division if slug provided
        loan_q = select(func.sum(Loan.outstanding_balance)).where(Loan.status == "active")
        if division_id is not None:
            loan_q = loan_q.where(Loan.division_id == division_id)
        loan_result = await session.execute(loan_q)
        loan_portfolio = float(loan_result.scalar() or 0.0)

        return KpiResponse(
            period=current_period,
            kpis={
                "total_revenue": KpiValue(
                    value=cur_revenue,
                    change_pct=_change_pct(cur_revenue, pri_revenue),
                ),
                "net_income": KpiValue(
                    value=cur_net_income,
                    change_pct=_change_pct(cur_net_income, pri_net_income),
                ),
                "total_assets": KpiValue(
                    value=cur_assets,
                    change_pct=_change_pct(cur_assets, pri_assets),
                ),
                "loan_portfolio": KpiValue(value=loan_portfolio, change_pct=0.0),
            },
        )


# ── Trends ────────────────────────────────────────────────────────────────────


class TrendPoint(BaseModel):
    period: str
    total_revenue: float
    net_income: float


class TrendsResponse(BaseModel):
    data: list[TrendPoint]


@router.get("/rollup/trends", response_model=TrendsResponse)
async def get_rollup_trends(
    _: dict = Depends(require_role(Role.CFO)),
    division_slug: Optional[str] = Query(default=None),
    from_period: Optional[str] = Query(default=None),
    to_period: Optional[str] = Query(default=None),
):
    async with AsyncSessionLocal() as session:
        # Resolve division_id if slug provided
        division_id = None
        if division_slug is not None:
            div_result = await session.execute(
                select(Division.id).where(Division.slug == division_slug)
            )
            row = div_result.fetchone()
            if row:
                division_id = row[0]

        rev_q = (
            select(FinancialStatement.period_label, func.sum(FinancialStatement.amount))
            .where(
                FinancialStatement.statement_type == "pnl",
                FinancialStatement.line_item == "Revenue",
            )
            .group_by(FinancialStatement.period_label)
            .order_by(FinancialStatement.period_label.desc())
        )
        ni_q = (
            select(FinancialStatement.period_label, func.sum(FinancialStatement.amount))
            .where(
                FinancialStatement.statement_type == "pnl",
                FinancialStatement.line_item == "Net Income",
            )
            .group_by(FinancialStatement.period_label)
            .order_by(FinancialStatement.period_label.desc())
        )

        if from_period:
            rev_q = rev_q.where(FinancialStatement.period_label >= from_period)
            ni_q = ni_q.where(FinancialStatement.period_label >= from_period)
        if to_period:
            rev_q = rev_q.where(FinancialStatement.period_label <= to_period)
            ni_q = ni_q.where(FinancialStatement.period_label <= to_period)
        if division_id is not None:
            rev_q = rev_q.where(FinancialStatement.division_id == division_id)
            ni_q = ni_q.where(FinancialStatement.division_id == division_id)

        rev_q = rev_q.limit(12)
        ni_q = ni_q.limit(12)

        rev_result = await session.execute(rev_q)
        ni_result = await session.execute(ni_q)

        rev_map = {row[0]: float(row[1] or 0) for row in rev_result.fetchall()}
        ni_map = {row[0]: float(row[1] or 0) for row in ni_result.fetchall()}

        all_periods = sorted(set(rev_map) | set(ni_map))
        data = [
            TrendPoint(
                period=p,
                total_revenue=rev_map.get(p, 0.0),
                net_income=ni_map.get(p, 0.0),
            )
            for p in all_periods
        ]
        return TrendsResponse(data=data)


# ── Division Comparison ───────────────────────────────────────────────────────


class DivisionKpi(BaseModel):
    name: str
    slug: str
    total_revenue: float
    net_income: float


class DivisionsResponse(BaseModel):
    period: str
    divisions: list[DivisionKpi]


@router.get("/rollup/divisions", response_model=DivisionsResponse)
async def get_rollup_divisions(
    _: dict = Depends(require_role(Role.CFO)),
    from_period: Optional[str] = Query(default=None),
    to_period: Optional[str] = Query(default=None),
):
    async with AsyncSessionLocal() as session:
        period_q = (
            select(FinancialStatement.period_label)
            .distinct()
            .order_by(FinancialStatement.period_label.desc())
            .limit(1)
        )
        if from_period:
            period_q = period_q.where(FinancialStatement.period_label >= from_period)
        if to_period:
            period_q = period_q.where(FinancialStatement.period_label <= to_period)

        period_result = await session.execute(period_q)
        row = period_result.fetchone()
        if not row:
            return DivisionsResponse(period="—", divisions=[])

        current_period = row[0]

        stmt = (
            select(
                Division.name,
                Division.slug,
                func.sum(
                    case(
                        (FinancialStatement.line_item == "Revenue", FinancialStatement.amount),
                        else_=0,
                    )
                ).label("total_revenue"),
                func.sum(
                    case(
                        (FinancialStatement.line_item == "Net Income", FinancialStatement.amount),
                        else_=0,
                    )
                ).label("net_income"),
            )
            .select_from(FinancialStatement)
            .join(Division, FinancialStatement.division_id == Division.id)
            .where(
                FinancialStatement.statement_type == "pnl",
                FinancialStatement.period_label == current_period,
            )
            .group_by(Division.id, Division.name, Division.slug)
            .order_by(
                func.sum(
                    case(
                        (FinancialStatement.line_item == "Revenue", FinancialStatement.amount),
                        else_=0,
                    )
                ).desc()
            )
        )
        result = await session.execute(stmt)
        divisions = [
            DivisionKpi(
                name=r.name,
                slug=r.slug,
                total_revenue=float(r.total_revenue or 0),
                net_income=float(r.net_income or 0),
            )
            for r in result.fetchall()
        ]
        return DivisionsResponse(period=current_period, divisions=divisions)

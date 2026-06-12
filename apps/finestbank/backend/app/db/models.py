import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Division(Base):
    __tablename__ = "divisions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    division_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("divisions.id"), index=True
    )
    type: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[str] = mapped_column(String(200))
    reference_id: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True
    )


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    division_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("divisions.id"), index=True
    )
    asset_name: Mapped[str] = mapped_column(String(100))
    asset_type: Mapped[str] = mapped_column(String(50))
    ticker: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    current_price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    market_value: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    weight_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    division_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("divisions.id"), index=True
    )
    borrower_name: Mapped[str] = mapped_column(String(100))
    loan_type: Mapped[str] = mapped_column(String(50))
    principal: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    outstanding_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    status: Mapped[str] = mapped_column(String(20))
    health_score: Mapped[int] = mapped_column(Integer())
    origination_date: Mapped[date] = mapped_column(Date)
    maturity_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    division_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("divisions.id"), index=True
    )
    statement_type: Mapped[str] = mapped_column(String(20))
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date] = mapped_column(Date)
    period_label: Mapped[str] = mapped_column(String(20))
    line_item: Mapped[str] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(50))
    resource: Mapped[str] = mapped_column(String(100))
    division_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("divisions.id"), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )

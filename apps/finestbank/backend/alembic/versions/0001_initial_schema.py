"""Initial schema: all tables, TimescaleDB hypertable, RLS policies

Revision ID: 0001
Revises:
Create Date: 2026-04-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- divisions -----------------------------------------------------------
    op.create_table(
        "divisions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_divisions_slug", "divisions", ["slug"], unique=True)

    # --- transactions (TimescaleDB hypertable) --------------------------------
    op.create_table(
        "transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("division_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("description", sa.String(200), nullable=False),
        sa.Column("reference_id", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="completed", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id"),
    )
    op.create_index("ix_transactions_division_id", "transactions", ["division_id"])
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])

    # Enable TimescaleDB hypertable on created_at
    op.execute(
        "SELECT create_hypertable('transactions', 'created_at', if_not_exists => TRUE)"
    )

    # --- portfolio_holdings ---------------------------------------------------
    op.create_table(
        "portfolio_holdings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("division_id", sa.UUID(), nullable=False),
        sa.Column("asset_name", sa.String(100), nullable=False),
        sa.Column("asset_type", sa.String(50), nullable=False),
        sa.Column("ticker", sa.String(20), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 6), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 2), nullable=False),
        sa.Column("current_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("market_value", sa.Numeric(18, 2), nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric(18, 2), nullable=False),
        sa.Column("weight_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_portfolio_holdings_division_id", "portfolio_holdings", ["division_id"]
    )

    # --- loans ---------------------------------------------------------------
    op.create_table(
        "loans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("division_id", sa.UUID(), nullable=False),
        sa.Column("borrower_name", sa.String(100), nullable=False),
        sa.Column("loan_type", sa.String(50), nullable=False),
        sa.Column("principal", sa.Numeric(18, 2), nullable=False),
        sa.Column("outstanding_balance", sa.Numeric(18, 2), nullable=False),
        sa.Column("interest_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("health_score", sa.Integer(), nullable=False),
        sa.Column("origination_date", sa.Date(), nullable=False),
        sa.Column("maturity_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_loans_division_id", "loans", ["division_id"])

    # --- financial_statements ------------------------------------------------
    op.create_table(
        "financial_statements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("division_id", sa.UUID(), nullable=False),
        sa.Column("statement_type", sa.String(20), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("period_label", sa.String(20), nullable=False),
        sa.Column("line_item", sa.String(100), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_financial_statements_division_id", "financial_statements", ["division_id"]
    )
    op.create_index(
        "ix_financial_statements_period_start",
        "financial_statements",
        ["period_start"],
    )

    # --- audit_logs ----------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("division_id", sa.UUID(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["division_id"], ["divisions.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- Row Level Security --------------------------------------------------
    # Apply RLS to all division-scoped tables (not audit_logs — superuser writes bypass)
    for table in ["transactions", "portfolio_holdings", "loans", "financial_statements"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY {table}_division_policy ON {table}
            USING (
                current_setting('app.role', true) = 'cfo'
                OR division_id::text = ANY(
                    string_to_array(current_setting('app.division_ids', true), ',')
                )
            )
            """
        )


def downgrade() -> None:
    # Drop RLS policies
    for table in ["transactions", "portfolio_holdings", "loans", "financial_statements"]:
        op.execute(f"DROP POLICY IF EXISTS {table}_division_policy ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.drop_table("audit_logs")
    op.drop_table("financial_statements")
    op.drop_table("loans")
    op.drop_table("portfolio_holdings")
    op.drop_table("transactions")
    op.drop_table("divisions")

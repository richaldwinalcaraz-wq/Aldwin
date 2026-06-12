"""
FinestBank seed script — populates all financial domains for all 4 divisions.

Run from backend/:
    python seed.py

Requires DATABASE_URL set in .env (asyncpg driver format).
"""
import asyncio
import os
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import asyncpg
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://finestbank:finestbank@localhost:5432/finestbank",
)
# asyncpg uses native postgres:// URL (not sqlalchemy+asyncpg://)
ASYNCPG_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace(
    "postgresql+psycopg2://", "postgresql://"
)

random.seed(42)
fake = Faker()
Faker.seed(42)

# Fixed UUIDs for reproducibility — do NOT change after first seed run
DIVISIONS = [
    {
        "id": "a1b2c3d4-0001-0001-0001-000000000001",
        "slug": "retail",
        "name": "Retail Banking",
    },
    {
        "id": "b2c3d4e5-0002-0002-0002-000000000002",
        "slug": "corporate",
        "name": "Corporate Banking",
    },
    {
        "id": "c3d4e5f6-0003-0003-0003-000000000003",
        "slug": "treasury",
        "name": "Treasury & Markets",
    },
    {
        "id": "d4e5f6a7-0004-0004-0004-000000000004",
        "slug": "wealth",
        "name": "Wealth Management",
    },
]

NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_datetime_last_n_days(n: int) -> datetime:
    delta = timedelta(seconds=random.randint(0, n * 86400))
    return NOW - delta


def rand_decimal(min_val: float, max_val: float, decimals: int = 2) -> Decimal:
    val = random.uniform(min_val, max_val)
    return Decimal(f"{val:.{decimals}f}")


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

CATEGORIES = ["deposit", "withdrawal", "transfer", "fee", "interest", "loan_payment"]
CATEGORY_WEIGHTS = [25, 20, 25, 10, 10, 10]

DESCRIPTIONS = {
    "deposit": [
        "Customer deposit",
        "Wire transfer inbound",
        "ACH deposit",
        "Payroll deposit",
    ],
    "withdrawal": [
        "ATM withdrawal",
        "Wire transfer outbound",
        "ACH withdrawal",
        "Cash withdrawal",
    ],
    "transfer": [
        "Inter-division transfer",
        "Cross-border payment",
        "Internal fund transfer",
        "Correspondent bank transfer",
    ],
    "fee": [
        "Monthly service fee",
        "Transaction fee",
        "Overdraft fee",
        "Wire fee",
    ],
    "interest": [
        "Interest income",
        "Interest payment",
        "Accrued interest",
        "Savings interest credit",
    ],
    "loan_payment": [
        "Loan principal payment",
        "Mortgage payment",
        "Commercial loan payment",
        "Credit line repayment",
    ],
}

STATUSES = ["completed", "pending", "failed"]
STATUS_WEIGHTS = [90, 8, 2]


def build_transactions(division_id: str, division_slug: str, count: int = 500) -> list:
    rows = []
    for _ in range(count):
        category = random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0]
        txn_type = "credit" if random.random() < 0.60 else "debit"
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        ref = f"TXN-{division_slug.upper()}-{str(uuid.uuid4())[:8].upper()}"
        rows.append(
            (
                str(uuid.uuid4()),                      # id
                division_id,                            # division_id
                txn_type,                               # type
                category,                               # category
                float(rand_decimal(100, 500_000)),      # amount
                "USD",                                  # currency
                random.choice(DESCRIPTIONS[category]),  # description
                ref,                                    # reference_id
                status,                                 # status
                rand_datetime_last_n_days(90),          # created_at
            )
        )
    return rows


# ---------------------------------------------------------------------------
# Portfolio Holdings
# ---------------------------------------------------------------------------

EQUITY_TICKERS = ["JPM", "GS", "BAC", "BRK.B", "MS", "C", "WFC", "BLK", "AXP", "COF"]
BOND_TICKERS = ["T-BOND-2030", "T-NOTE-2027", "CORP-AAA-2028", "MUNI-2032", "T-BILL-6M"]
ASSET_TYPES = ["equity", "bond", "cash", "real_estate", "commodity"]
ASSET_WEIGHTS_BY_TYPE = [40, 30, 15, 10, 5]


def build_holdings(division_id: str, count: int = 20) -> list:
    rows = []
    raw_weights = []

    for _ in range(count):
        asset_type = random.choices(ASSET_TYPES, weights=ASSET_WEIGHTS_BY_TYPE)[0]

        if asset_type == "equity":
            ticker = random.choice(EQUITY_TICKERS)
            asset_name = f"{ticker} Common Stock"
        elif asset_type == "bond":
            ticker = random.choice(BOND_TICKERS)
            asset_name = f"{ticker} Bond"
        elif asset_type == "cash":
            ticker = None
            asset_name = "Cash & Equivalents"
        elif asset_type == "real_estate":
            ticker = None
            asset_name = fake.city() + " Commercial Property"
        else:  # commodity
            ticker = None
            asset_name = random.choice(["Gold", "Silver", "Crude Oil", "Copper", "Natural Gas"])

        unit_cost = float(rand_decimal(10, 10_000))
        price_change = random.uniform(-0.20, 0.20)
        current_price = unit_cost * (1 + price_change)
        quantity = random.uniform(10, 10_000)
        market_value = current_price * quantity
        unrealized_pnl = (current_price - unit_cost) * quantity
        raw_weight = market_value
        raw_weights.append(raw_weight)

        rows.append(
            [
                str(uuid.uuid4()),       # id
                division_id,             # division_id
                asset_name,              # asset_name
                asset_type,              # asset_type
                ticker,                  # ticker (nullable)
                round(quantity, 6),      # quantity
                round(unit_cost, 2),     # unit_cost
                round(current_price, 2), # current_price
                round(market_value, 2),  # market_value
                round(unrealized_pnl, 2),# unrealized_pnl
                0.0,                     # weight_pct (filled below)
                NOW,                     # updated_at
            ]
        )

    total_weight = sum(raw_weights)
    for i, row in enumerate(rows):
        row[10] = round((raw_weights[i] / total_weight) * 100, 2)

    return [tuple(r) for r in rows]


# ---------------------------------------------------------------------------
# Loans
# ---------------------------------------------------------------------------

LOAN_TYPES = ["mortgage", "commercial", "personal", "auto", "credit_line"]
LOAN_TYPE_WEIGHTS = [30, 35, 20, 10, 5]
LOAN_STATUSES = ["active", "delinquent", "paid_off", "defaulted"]
LOAN_STATUS_WEIGHTS = [80, 10, 7, 3]


def build_loans(division_id: str, count: int = 15) -> list:
    rows = []
    for _ in range(count):
        loan_type = random.choices(LOAN_TYPES, weights=LOAN_TYPE_WEIGHTS)[0]
        status = random.choices(LOAN_STATUSES, weights=LOAN_STATUS_WEIGHTS)[0]

        # Health score: mostly healthy, some distressed
        if status == "active":
            health_score = random.choices(
                [random.randint(70, 100), random.randint(50, 69)],
                weights=[85, 15],
            )[0]
        elif status == "delinquent":
            health_score = random.randint(20, 50)
        elif status == "defaulted":
            health_score = random.randint(1, 25)
        else:  # paid_off
            health_score = random.randint(80, 100)

        principal = float(rand_decimal(50_000, 10_000_000))
        balance_pct = random.uniform(0.10, 0.95)
        outstanding_balance = round(principal * balance_pct, 2)
        interest_rate = round(random.uniform(0.0350, 0.1200), 4)

        days_ago = random.randint(365, 365 * 5)
        origination_date = (NOW - timedelta(days=days_ago)).date()
        maturity_years = random.randint(1, 20)
        maturity_date = date(
            origination_date.year + maturity_years,
            origination_date.month,
            origination_date.day,
        )

        rows.append(
            (
                str(uuid.uuid4()),        # id
                division_id,              # division_id
                fake.name(),              # borrower_name
                loan_type,                # loan_type
                round(principal, 2),      # principal
                outstanding_balance,      # outstanding_balance
                interest_rate,            # interest_rate
                status,                   # status
                health_score,             # health_score
                origination_date,         # origination_date
                maturity_date,            # maturity_date
                NOW,                      # created_at
            )
        )
    return rows


# ---------------------------------------------------------------------------
# Financial Statements
# ---------------------------------------------------------------------------

PNL_ITEMS = ["Revenue", "COGS", "Gross Profit", "Operating Expenses", "EBITDA", "Net Income"]
BALANCE_ITEMS = [
    "Total Assets",
    "Total Liabilities",
    "Equity",
    "Cash & Equivalents",
    "Loans Receivable",
    "Securities",
]
CASHFLOW_ITEMS = [
    "Operating Cash Flow",
    "Investing Activities",
    "Financing Activities",
    "Net Cash Flow",
]

# Division-level revenue scale ($M)
DIVISION_REVENUE_BASE = {
    "retail": (10_000_000, 50_000_000),
    "corporate": (20_000_000, 80_000_000),
    "treasury": (5_000_000, 30_000_000),
    "wealth": (8_000_000, 40_000_000),
}


def build_financial_statements(division_id: str, division_slug: str) -> list:
    rows = []
    rev_min, rev_max = DIVISION_REVENUE_BASE.get(
        division_slug, (5_000_000, 50_000_000)
    )

    # Generate 12 months of each statement type
    base_revenue = random.uniform(rev_min, rev_max)

    for months_ago in range(12, 0, -1):
        # Calculate period
        period_end_dt = NOW - timedelta(days=months_ago * 30)
        period_start = date(period_end_dt.year, period_end_dt.month, 1)
        # Last day of month
        if period_end_dt.month == 12:
            period_end = date(period_end_dt.year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(
                period_end_dt.year, period_end_dt.month + 1, 1
            ) - timedelta(days=1)
        period_label = period_start.strftime("%Y-%m")

        # Apply slight MoM growth with noise
        growth = 1 + random.uniform(-0.02, 0.04)
        base_revenue *= growth

        # P&L
        revenue = base_revenue
        cogs = revenue * random.uniform(0.40, 0.60)
        gross_profit = revenue - cogs
        opex = revenue * random.uniform(0.20, 0.35)
        ebitda = gross_profit - opex
        net_income = ebitda * random.uniform(0.60, 0.85)

        pnl_values = {
            "Revenue": revenue,
            "COGS": -cogs,
            "Gross Profit": gross_profit,
            "Operating Expenses": -opex,
            "EBITDA": ebitda,
            "Net Income": net_income,
        }
        for line_item, amount in pnl_values.items():
            rows.append(
                (
                    str(uuid.uuid4()),
                    division_id,
                    "pnl",
                    period_start,
                    period_end,
                    period_label,
                    line_item,
                    round(amount, 2),
                    NOW,
                )
            )

        # Balance Sheet
        total_assets = revenue * random.uniform(8, 15)
        total_liabilities = total_assets * random.uniform(0.50, 0.75)
        equity = total_assets - total_liabilities
        cash = total_assets * random.uniform(0.05, 0.15)
        loans_receivable = total_assets * random.uniform(0.30, 0.50)
        securities = total_assets * random.uniform(0.20, 0.35)

        bs_values = {
            "Total Assets": total_assets,
            "Total Liabilities": -total_liabilities,
            "Equity": equity,
            "Cash & Equivalents": cash,
            "Loans Receivable": loans_receivable,
            "Securities": securities,
        }
        for line_item, amount in bs_values.items():
            rows.append(
                (
                    str(uuid.uuid4()),
                    division_id,
                    "balance_sheet",
                    period_start,
                    period_end,
                    period_label,
                    line_item,
                    round(amount, 2),
                    NOW,
                )
            )

        # Cash Flow
        operating_cf = net_income * random.uniform(1.0, 1.4)
        investing_cf = -revenue * random.uniform(0.02, 0.10)
        financing_cf = -revenue * random.uniform(0.01, 0.05)
        net_cf = operating_cf + investing_cf + financing_cf

        cf_values = {
            "Operating Cash Flow": operating_cf,
            "Investing Activities": investing_cf,
            "Financing Activities": financing_cf,
            "Net Cash Flow": net_cf,
        }
        for line_item, amount in cf_values.items():
            rows.append(
                (
                    str(uuid.uuid4()),
                    division_id,
                    "cash_flow",
                    period_start,
                    period_end,
                    period_label,
                    line_item,
                    round(amount, 2),
                    NOW,
                )
            )

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed():
    print("Connecting to database...")
    conn = await asyncpg.connect(ASYNCPG_URL)

    try:
        print("Truncating all tables...")
        await conn.execute(
            "TRUNCATE divisions, transactions, portfolio_holdings, loans, "
            "financial_statements, audit_logs RESTART IDENTITY CASCADE"
        )

        # --- Divisions -------------------------------------------------------
        print("Seeding divisions...")
        await conn.executemany(
            "INSERT INTO divisions (id, slug, name) VALUES ($1, $2, $3)",
            [(d["id"], d["slug"], d["name"]) for d in DIVISIONS],
        )

        # --- Per-division data -----------------------------------------------
        for division in DIVISIONS:
            div_id = division["id"]
            div_slug = division["slug"]

            print(f"Seeding transactions ({div_slug})...")
            txns = build_transactions(div_id, div_slug, count=500)
            await conn.executemany(
                """
                INSERT INTO transactions
                    (id, division_id, type, category, amount, currency,
                     description, reference_id, status, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                txns,
            )

            print(f"Seeding portfolio holdings ({div_slug})...")
            holdings = build_holdings(div_id, count=20)
            await conn.executemany(
                """
                INSERT INTO portfolio_holdings
                    (id, division_id, asset_name, asset_type, ticker,
                     quantity, unit_cost, current_price, market_value,
                     unrealized_pnl, weight_pct, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                holdings,
            )

            print(f"Seeding loans ({div_slug})...")
            loans = build_loans(div_id, count=15)
            await conn.executemany(
                """
                INSERT INTO loans
                    (id, division_id, borrower_name, loan_type, principal,
                     outstanding_balance, interest_rate, status, health_score,
                     origination_date, maturity_date, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                loans,
            )

            print(f"Seeding financial statements ({div_slug})...")
            statements = build_financial_statements(div_id, div_slug)
            await conn.executemany(
                """
                INSERT INTO financial_statements
                    (id, division_id, statement_type, period_start, period_end,
                     period_label, line_item, amount, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                statements,
            )

        # --- Final counts ----------------------------------------------------
        print("\n--- Seed complete ---")
        for table in [
            "divisions",
            "transactions",
            "portfolio_holdings",
            "loans",
            "financial_statements",
            "audit_logs",
        ]:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {count} rows")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())

"""Nirnaya — Finance Engine.

Deterministic financial calculations: categorization, spending analysis,
goal tracking, and scenario simulation.

All financial math is pure Python. No LLM involved.
"""

import csv
import io
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas import (
    TransactionSchema, TransactionUploadResponse,
    SpendingSummary, GoalCreateRequest, GoalResponse,
    GoalSimulateRequest, GoalSimulateResponse,
)
from app.models import Transaction, Goal, User

logger = logging.getLogger(__name__)


# ─── Transaction Categorization ─────────────────────────────
# Deterministic keyword-based categorization (P0).
# ML categorization comes in Phase 8.

CATEGORY_RULES: Dict[str, List[str]] = {
    "food": [
        "swiggy", "zomato", "restaurant", "cafe", "food", "pizza", "burger",
        "biryani", "chicken", "dining", "eat", "meal", "lunch", "dinner",
        "breakfast", "snack", "bakery", "tea", "coffee", "starbucks",
        "dominos", "mcdonalds", "kfc", "subway", "hotel",
    ],
    "transport": [
        "uber", "ola", "rapido", "metro", "bus", "train", "irctc", "fuel",
        "petrol", "diesel", "parking", "toll", "cab", "auto", "rickshaw",
        "flight", "airline", "indigo", "spicejet", "makemytrip",
    ],
    "shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "shopping",
        "clothes", "shoes", "electronics", "mobile", "laptop", "reliance",
        "dmart", "big bazaar", "mall", "store", "mart", "purchase",
    ],
    "utilities": [
        "electricity", "water", "gas", "broadband", "internet", "wifi",
        "jio", "airtel", "vodafone", "vi ", "bsnl", "phone bill",
        "recharge", "postpaid", "prepaid", "dth", "tata sky",
    ],
    "rent": [
        "rent", "landlord", "house rent", "accommodation", "pg ", "hostel",
        "flat rent", "room rent",
    ],
    "health": [
        "hospital", "doctor", "medicine", "pharmacy", "medical",
        "diagnostic", "lab test", "apollo", "fortis", "medplus",
        "practo", "1mg", "netmeds", "health", "gym", "fitness",
    ],
    "education": [
        "school", "college", "university", "tuition", "course", "udemy",
        "coursera", "book", "stationery", "exam", "fee", "coaching",
    ],
    "entertainment": [
        "netflix", "spotify", "prime video", "hotstar", "disney",
        "movie", "cinema", "pvr", "inox", "game", "subscription",
        "youtube", "concert", "event",
    ],
    "investment": [
        "mutual fund", "sip", "zerodha", "groww", "upstox", "stocks",
        "shares", "fd ", "fixed deposit", "rd ", "recurring deposit",
        "ppf", "nps", "investment", "trading",
    ],
    "insurance": [
        "insurance", "lic", "premium", "policy", "term plan",
        "health insurance", "motor insurance",
    ],
    "transfers": [
        "transfer", "neft", "rtgs", "imps", "upi", "sent to",
        "paid to", "credited", "debited",
    ],
    "emi": [
        "emi", "loan", "installment", "bajaj finserv", "hdfc loan",
        "personal loan", "home loan", "car loan",
    ],
    "salary": [
        "salary", "payroll", "wages", "stipend", "income",
    ],
}


def categorize_transaction(description: str, payee: str = "") -> str:
    """Categorize a transaction based on description and payee keywords.
    
    Returns the most likely category or 'other'.
    """
    text = f"{description} {payee}".lower().strip()
    if not text:
        return "other"

    # Count matching keywords per category
    scores: Dict[str, int] = {}
    for category, keywords in CATEGORY_RULES.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)
    return "other"


async def ensure_user(user_id: str, db: AsyncSession) -> User:
    """Get or create a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id, name=f"User {user_id[:8]}")
        db.add(user)
        await db.flush()
    return user


async def upload_transactions(
    user_id: str,
    csv_content: str,
    db: AsyncSession,
) -> TransactionUploadResponse:
    """Parse and import transactions from CSV content.
    
    Expected CSV columns: date, amount, payee, description
    Optional: category, type (income/expense)
    """
    await ensure_user(user_id, db)

    reader = csv.DictReader(io.StringIO(csv_content))
    imported = 0
    skipped = 0
    categories: Dict[str, int] = defaultdict(int)
    dates: List[datetime] = []

    for row in reader:
        try:
            # Parse amount
            amount_str = row.get("amount", "0").strip().replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "")
            # Handle negative amounts or debit indicators
            is_debit = False
            if amount_str.startswith("-"):
                is_debit = True
                amount_str = amount_str[1:]
            elif amount_str.startswith("(") and amount_str.endswith(")"):
                is_debit = True
                amount_str = amount_str[1:-1]
            
            amount = float(amount_str)
            if amount == 0:
                skipped += 1
                continue

            # Parse date (try multiple formats)
            date_str = row.get("date", "").strip()
            txn_date = None
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%b-%Y", "%d %b %Y"]:
                try:
                    txn_date = datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue
            
            if txn_date is None:
                skipped += 1
                continue

            # Determine if income
            txn_type = row.get("type", "").strip().lower()
            is_income = txn_type in ("income", "credit", "cr") or (not is_debit and "salary" in row.get("description", "").lower())

            # Categorize
            payee = row.get("payee", "").strip()
            description = row.get("description", "").strip()
            category = row.get("category", "").strip()
            if not category:
                category = categorize_transaction(description, payee)

            txn = Transaction(
                user_id=user_id,
                amount=amount,
                category=category,
                payee=payee,
                description=description,
                transaction_date=txn_date,
                source="csv",
                is_income=is_income,
            )
            db.add(txn)
            imported += 1
            categories[category] += 1
            dates.append(txn_date)

        except Exception as e:
            logger.warning(f"Skipped row: {e}")
            skipped += 1
            continue

    await db.flush()

    date_range = {}
    if dates:
        date_range = {
            "start": min(dates).strftime("%Y-%m-%d"),
            "end": max(dates).strftime("%Y-%m-%d"),
        }

    logger.info(f"Imported {imported} transactions for user {user_id}, skipped {skipped}")

    return TransactionUploadResponse(
        imported=imported,
        skipped=skipped,
        categories=dict(categories),
        date_range=date_range,
        user_id=user_id,
    )


async def get_spending_summary(
    user_id: str,
    db: AsyncSession,
) -> SpendingSummary:
    """Calculate spending summary from transaction history."""
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user_id)
    )
    transactions = result.scalars().all()

    if not transactions:
        return SpendingSummary(
            user_id=user_id,
            period="monthly",
            total_income=0,
            total_expenses=0,
            monthly_surplus=0,
            by_category={},
            monthly_trends=[],
            top_payees=[],
        )

    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.is_income)
    total_expenses = sum(t.amount for t in transactions if not t.is_income)

    # By category (expenses only)
    by_category: Dict[str, float] = defaultdict(float)
    for t in transactions:
        if not t.is_income:
            by_category[t.category or "other"] += t.amount

    # Monthly trends
    monthly: Dict[str, Dict[str, float]] = defaultdict(lambda: {"income": 0, "expenses": 0})
    for t in transactions:
        month_key = t.transaction_date.strftime("%Y-%m")
        if t.is_income:
            monthly[month_key]["income"] += t.amount
        else:
            monthly[month_key]["expenses"] += t.amount

    monthly_trends = [
        {"month": k, "income": v["income"], "expenses": v["expenses"],
         "surplus": v["income"] - v["expenses"]}
        for k, v in sorted(monthly.items())
    ]

    # Calculate monthly averages
    num_months = len(monthly) or 1
    avg_monthly_income = total_income / num_months
    avg_monthly_expenses = total_expenses / num_months
    monthly_surplus = avg_monthly_income - avg_monthly_expenses

    # Top payees
    payee_totals: Dict[str, float] = defaultdict(float)
    for t in transactions:
        if not t.is_income and t.payee:
            payee_totals[t.payee] += t.amount
    top_payees = [
        {"payee": k, "total": v}
        for k, v in sorted(payee_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    return SpendingSummary(
        user_id=user_id,
        period="monthly",
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        monthly_surplus=round(monthly_surplus, 2),
        by_category={k: round(v, 2) for k, v in sorted(by_category.items(), key=lambda x: x[1], reverse=True)},
        monthly_trends=monthly_trends,
        top_payees=top_payees,
    )


async def create_goal(
    request: GoalCreateRequest,
    db: AsyncSession,
) -> GoalResponse:
    """Create a financial goal."""
    await ensure_user(request.user_id, db)

    goal = Goal(
        user_id=request.user_id,
        name=request.name,
        target_amount=request.target_amount,
        current_amount=request.current_amount,
        deadline=request.deadline,
        priority=request.priority,
    )
    db.add(goal)
    await db.flush()

    return _goal_to_response(goal, monthly_surplus=None)


async def get_goals(user_id: str, db: AsyncSession) -> List[GoalResponse]:
    """Get all goals for a user."""
    result = await db.execute(select(Goal).where(Goal.user_id == user_id))
    goals = result.scalars().all()

    # Get monthly surplus for progress calculation
    spending = await get_spending_summary(user_id, db)

    return [_goal_to_response(g, spending.monthly_surplus) for g in goals]


async def simulate_goal(
    goal_id: str,
    request: GoalSimulateRequest,
    db: AsyncSession,
) -> GoalSimulateResponse:
    """Simulate the effect of a spending change on a goal.
    
    All calculations are deterministic Python math.
    """
    # Get goal
    result = await db.execute(select(Goal).where(Goal.id == goal_id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise ValueError(f"Goal {goal_id} not found")

    # Get current spending
    spending = await get_spending_summary(request.user_id, db)
    current_surplus = spending.monthly_surplus

    # Parse scenario
    scenario = request.scenario
    reduce_category = scenario.get("reduce_category", "")
    reduce_by = float(scenario.get("reduce_by", 0))
    additional_income = float(scenario.get("additional_income", 0))

    new_surplus = current_surplus + reduce_by + additional_income

    # Calculate timelines
    remaining = goal.target_amount - goal.current_amount
    
    current_months = _months_to_goal(remaining, current_surplus) if current_surplus > 0 else None
    new_months = _months_to_goal(remaining, new_surplus) if new_surplus > 0 else None

    # Projected date
    projected_date = None
    if new_months is not None:
        from datetime import timedelta
        projected = datetime.now(timezone.utc) + timedelta(days=new_months * 30)
        projected_date = projected.strftime("%Y-%m-%d")

    # Scenario description
    parts = []
    if reduce_by > 0 and reduce_category:
        parts.append(f"Reduce {reduce_category} spending by ₹{reduce_by:,.0f}/month")
    if additional_income > 0:
        parts.append(f"Add ₹{additional_income:,.0f}/month income")
    scenario_desc = "; ".join(parts) if parts else "No changes"

    return GoalSimulateResponse(
        goal_id=goal_id,
        goal_name=goal.name,
        current_monthly_savings=round(current_surplus, 2),
        new_monthly_savings=round(new_surplus, 2),
        current_months_to_goal=current_months,
        new_months_to_goal=new_months,
        savings_difference=round(new_surplus - current_surplus, 2),
        projected_goal_date=projected_date,
        scenario_description=scenario_desc,
    )


def _months_to_goal(remaining: float, monthly_savings: float) -> Optional[int]:
    """Calculate months needed to reach a goal given monthly savings."""
    if monthly_savings <= 0:
        return None
    import math
    return math.ceil(remaining / monthly_savings)


def _goal_to_response(goal: Goal, monthly_surplus: Optional[float]) -> GoalResponse:
    """Convert a Goal model to GoalResponse."""
    progress_pct = 0.0
    if goal.target_amount > 0:
        progress_pct = round((goal.current_amount / goal.target_amount) * 100, 1)

    remaining = goal.target_amount - goal.current_amount
    monthly_required = None
    months_remaining = None
    on_track = None

    if goal.deadline:
        deadline = goal.deadline
        # Ensure timezone-aware comparison
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        months_left = max(1, (deadline - datetime.now(timezone.utc)).days / 30)
        monthly_required = round(remaining / months_left, 2)
        if monthly_surplus is not None:
            on_track = monthly_surplus >= monthly_required
            months_remaining = _months_to_goal(remaining, monthly_surplus)

    return GoalResponse(
        id=goal.id,
        user_id=goal.user_id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        deadline=goal.deadline,
        priority=goal.priority,
        progress_pct=progress_pct,
        monthly_required=monthly_required,
        months_remaining=months_remaining,
        on_track=on_track,
        created_at=goal.created_at or datetime.now(timezone.utc),
    )

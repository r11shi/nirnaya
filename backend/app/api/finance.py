"""Nirnaya — Finance API Routes."""

import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    SpendingSummary, GoalCreateRequest, GoalResponse,
    GoalSimulateRequest, GoalSimulateResponse,
    TransactionUploadResponse,
)
from app.services.finance_engine import (
    upload_transactions, get_spending_summary,
    create_goal, get_goals, simulate_goal,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/finance", tags=["finance"])


@router.post("/transactions/upload", response_model=TransactionUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    user_id: str = Form(default="default-user"),
    db: AsyncSession = Depends(get_db),
):
    """Upload transactions from a CSV file.
    
    Expected columns: date, amount, payee, description
    Optional: category, type (income/expense)
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    content = await file.read()
    try:
        csv_text = content.decode("utf-8")
    except UnicodeDecodeError:
        csv_text = content.decode("latin-1")

    try:
        result = await upload_transactions(user_id, csv_text, db)
        return result
    except Exception as e:
        logger.error(f"Transaction upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/spending/{user_id}", response_model=SpendingSummary)
async def spending(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get spending summary for a user."""
    try:
        return await get_spending_summary(user_id, db)
    except Exception as e:
        logger.error(f"Spending summary failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goals", response_model=GoalResponse)
async def create_new_goal(
    request: GoalCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new financial goal."""
    try:
        return await create_goal(request, db)
    except Exception as e:
        logger.error(f"Goal creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals/{user_id}")
async def list_goals(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all goals for a user."""
    try:
        goals = await get_goals(user_id, db)
        return {"goals": [g.model_dump() for g in goals]}
    except Exception as e:
        logger.error(f"Goal listing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goals/{goal_id}/simulate", response_model=GoalSimulateResponse)
async def simulate(
    goal_id: str,
    request: GoalSimulateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Simulate the effect of a spending change on a goal."""
    try:
        return await simulate_goal(goal_id, request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Goal simulation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

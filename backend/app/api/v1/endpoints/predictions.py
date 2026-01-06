from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select, update, delete
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

from app.api.v1.deps import CurrentUser, DBSession
from app.models import Prediction, User
from app.schemas.prediction import (
    PredictionCreate,
    PredictionUpdate,
    PredictionResponse,
    PredictionListResponse,
    PredictionActionRequest,
    PredictionStatsResponse,
)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    type: Optional[str] = None,
    impact: Optional[str] = None,
):
    """List all predictions for the organization."""
    query = select(Prediction).where(
        Prediction.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.where(Prediction.status == status)
    if type:
        query = query.where(Prediction.type == type)
    if impact:
        query = query.where(Prediction.impact == impact)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id
        )
    )
    total = count_result.scalar()
    
    # Get predictions with pagination
    result = await db.execute(
        query.order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
    )
    predictions = result.scalars().all()
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": predictions,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@router.get("/stats", response_model=PredictionStatsResponse)
async def get_prediction_stats(
    db: DBSession,
    current_user: CurrentUser,
):
    """Get prediction statistics."""
    base_query = select(Prediction).where(
        Prediction.organization_id == current_user.organization_id
    )
    
    # Get total count
    total_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id
        )
    )
    total_predictions = total_result.scalar()
    
    # Get active count
    active_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id,
            Prediction.status == "active"
        )
    )
    active_predictions = active_result.scalar()
    
    # Get prevented count
    prevented_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id,
            Prediction.status == "prevented"
        )
    )
    prevented_count = prevented_result.scalar()
    
    # Get occurred count
    occurred_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id,
            Prediction.status == "occurred"
        )
    )
    occurred_count = occurred_result.scalar()
    
    # Get expired count
    expired_result = await db.execute(
        select(func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id,
            Prediction.status == "expired"
        )
    )
    expired_count = expired_result.scalar()
    
    # Calculate average likelihood for active predictions
    active_preds_result = await db.execute(
        select(Prediction).where(
            Prediction.organization_id == current_user.organization_id,
            Prediction.status == "active"
        )
    )
    active_preds = active_preds_result.scalars().all()
    avg_likelihood = 0.0
    if active_preds:
        avg_likelihood = sum(float(p.likelihood) for p in active_preds) / len(active_preds)
    
    # Group by type
    by_type = {}
    type_counts_result = await db.execute(
        select(Prediction.type, func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id
        ).group_by(Prediction.type)
    )
    type_counts = type_counts_result.all()
    
    for pred_type, count in type_counts:
        by_type[pred_type] = count
    
    # Group by impact
    by_impact = {}
    impact_counts_result = await db.execute(
        select(Prediction.impact, func.count(Prediction.id)).where(
            Prediction.organization_id == current_user.organization_id
        ).group_by(Prediction.impact)
    )
    impact_counts = impact_counts_result.all()
    
    for impact, count in impact_counts:
        by_impact[impact] = count
    
    return {
        "total_predictions": total_predictions,
        "active_predictions": active_predictions,
        "prevented_count": prevented_count,
        "occurred_count": occurred_count,
        "expired_count": expired_count,
        "avg_likelihood": avg_likelihood,
        "by_type": by_type,
        "by_impact": by_impact,
    }


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_in: PredictionCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Create a new prediction (typically called by AI service)."""
    prediction = Prediction(
        organization_id=current_user.organization_id,
        status="active",
        **prediction_in.dict(),
    )
    db.add(prediction)
    await db.commit()
    await db.refresh(prediction)
    return prediction


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific prediction."""
    result = await db.execute(
        select(Prediction).where(
            Prediction.id == prediction_id,
            Prediction.organization_id == current_user.organization_id,
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    return prediction


@router.put("/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: UUID,
    prediction_in: PredictionUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update a prediction."""
    result = await db.execute(
        select(Prediction).where(
            Prediction.id == prediction_id,
            Prediction.organization_id == current_user.organization_id,
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    update_data = prediction_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prediction, field, value)
    
    await db.commit()
    await db.refresh(prediction)
    return prediction


@router.post("/{prediction_id}/take-action", response_model=PredictionResponse)
async def take_action_on_prediction(
    prediction_id: UUID,
    action_request: PredictionActionRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """Mark a prediction as prevented by taking action."""
    result = await db.execute(
        select(Prediction).where(
            Prediction.id == prediction_id,
            Prediction.organization_id == current_user.organization_id,
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    if prediction.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only take action on active predictions",
        )
    
    prediction.status = "prevented"
    prediction.action_taken = action_request.action_taken
    prediction.action_taken_at = datetime.now(timezone.utc)
    prediction.action_taken_by_id = current_user.id
    
    await db.commit()
    await db.refresh(prediction)
    return prediction


@router.post("/{prediction_id}/dismiss", response_model=PredictionResponse)
async def dismiss_prediction(
    prediction_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Dismiss a prediction."""
    result = await db.execute(
        select(Prediction).where(
            Prediction.id == prediction_id,
            Prediction.organization_id == current_user.organization_id,
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    if prediction.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only dismiss active predictions",
        )
    
    prediction.status = "expired"
    
    await db.commit()
    await db.refresh(prediction)
    return prediction


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Delete a prediction."""
    result = await db.execute(
        select(Prediction).where(
            Prediction.id == prediction_id,
            Prediction.organization_id == current_user.organization_id,
        )
    )
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    await db.execute(delete(Prediction).where(Prediction.id == prediction_id))
    await db.commit()

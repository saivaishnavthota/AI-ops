from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from typing import List, Dict, Any
from datetime import datetime

from app.config.database import get_db
from app.api.v1.deps import CurrentUser
from app.models.cloud import (
    CloudResource,
    CloudCostItem,
    CloudOptimizationRecommendation,
    ResourceStatus,
    RecommendationStatus
)

router = APIRouter(prefix="/cloud", tags=["Cloud"])


@router.get("/resources")
async def list_cloud_resources(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all cloud resources for the organization."""
    
    query = select(CloudResource).where(
        CloudResource.organization_id == current_user.organization_id
    ).order_by(CloudResource.created_at.desc())
    
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return [
        {
            "id": str(resource.id),
            "name": resource.name,
            "type": resource.resource_type,
            "provider": resource.provider,
            "region": resource.region,
            "status": resource.status.value,
            "cpu": resource.cpu_usage,
            "memory": resource.memory_usage,
            "cost": resource.monthly_cost,
            "instanceType": resource.instance_type,
            "privateIp": resource.private_ip,
            "publicIp": resource.public_ip,
            "launchTime": resource.launch_time.isoformat() if resource.launch_time else None,
        }
        for resource in resources
    ]


@router.get("/costs")
async def list_cloud_costs(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get cloud cost breakdown."""
    
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    query = select(CloudCostItem).where(
        CloudCostItem.organization_id == current_user.organization_id,
        CloudCostItem.month == current_month,
        CloudCostItem.year == current_year
    ).order_by(CloudCostItem.current_month.desc())
    
    result = await db.execute(query)
    costs = result.scalars().all()
    
    return [
        {
            "id": str(cost.id),
            "service": cost.service,
            "category": cost.category,
            "currentMonth": cost.current_month,
            "lastMonth": cost.last_month,
            "change": ((cost.current_month - cost.last_month) / cost.last_month * 100) if cost.last_month > 0 else 0,
            "budget": cost.budget,
            "details": cost.details,
        }
        for cost in costs
    ]


@router.get("/optimization-recommendations")
async def list_optimization_recommendations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get cloud optimization recommendations."""
    
    query = select(CloudOptimizationRecommendation).where(
        CloudOptimizationRecommendation.organization_id == current_user.organization_id
    ).order_by(
        CloudOptimizationRecommendation.monthly_savings.desc()
    )
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    
    return [
        {
            "id": str(rec.id),
            "type": rec.recommendation_type,
            "resource": rec.resource_name,
            "description": rec.description,
            "impact": rec.impact.value,
            "savings": rec.monthly_savings,
            "effort": rec.effort,
            "status": rec.status.value,
            "aiConfidence": rec.ai_confidence,
            "steps": rec.implementation_steps,
        }
        for rec in recommendations
    ]


@router.post("/optimization-recommendations/{recommendation_id}/apply")
async def apply_optimization_recommendation(
    recommendation_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Apply an optimization recommendation."""
    
    from uuid import UUID
    
    query = select(CloudOptimizationRecommendation).where(
        CloudOptimizationRecommendation.id == UUID(recommendation_id),
        CloudOptimizationRecommendation.organization_id == current_user.organization_id
    )
    
    result = await db.execute(query)
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = RecommendationStatus.APPLIED
    recommendation.applied_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Optimization applied successfully", "savings": recommendation.monthly_savings}


@router.post("/optimization-recommendations/{recommendation_id}/dismiss")
async def dismiss_optimization_recommendation(
    recommendation_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Dismiss an optimization recommendation."""
    
    from uuid import UUID
    
    query = select(CloudOptimizationRecommendation).where(
        CloudOptimizationRecommendation.id == UUID(recommendation_id),
        CloudOptimizationRecommendation.organization_id == current_user.organization_id
    )
    
    result = await db.execute(query)
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = RecommendationStatus.DISMISSED
    recommendation.dismissed_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Recommendation dismissed"}


@router.post("/resources/{resource_id}/start")
async def start_cloud_resource(
    resource_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Start a cloud resource."""
    
    from uuid import UUID
    
    query = select(CloudResource).where(
        CloudResource.id == UUID(resource_id),
        CloudResource.organization_id == current_user.organization_id
    )
    
    result = await db.execute(query)
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.status = ResourceStatus.RUNNING
    resource.cpu_usage = 25.0
    resource.memory_usage = 35.0
    
    await db.commit()
    
    return {"message": f"{resource.name} started successfully"}


@router.post("/resources/{resource_id}/stop")
async def stop_cloud_resource(
    resource_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Stop a cloud resource."""
    
    from uuid import UUID
    
    query = select(CloudResource).where(
        CloudResource.id == UUID(resource_id),
        CloudResource.organization_id == current_user.organization_id
    )
    
    result = await db.execute(query)
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.status = ResourceStatus.STOPPED
    resource.cpu_usage = 0
    resource.memory_usage = 0
    resource.monthly_cost = 0
    
    await db.commit()
    
    return {"message": f"{resource.name} stopped"}


@router.post("/resources/{resource_id}/reboot")
async def reboot_cloud_resource(
    resource_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Reboot a cloud resource."""
    
    from uuid import UUID
    
    query = select(CloudResource).where(
        CloudResource.id == UUID(resource_id),
        CloudResource.organization_id == current_user.organization_id
    )
    
    result = await db.execute(query)
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    resource.status = ResourceStatus.PENDING
    
    await db.commit()
    await db.refresh(resource)
    
    # Simulate reboot completion
    resource.status = ResourceStatus.RUNNING
    await db.commit()
    
    return {"message": f"{resource.name} rebooted successfully"}

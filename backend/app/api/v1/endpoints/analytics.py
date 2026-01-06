from fastapi import APIRouter, Depends
from sqlalchemy import func, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.config.database import get_db
from app.models.incident import Incident, IncidentStatus
from app.models.alert import Alert, AlertStatus, AlertSeverity
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_analytics_overview(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics overview data."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get incident statistics
    from sqlalchemy import select
    
    # Total incidents
    total_incidents_query = select(func.count(Incident.id)).where(
        Incident.created_at >= start_date
    )
    total_incidents_result = await db.execute(total_incidents_query)
    total_incidents = total_incidents_result.scalar() or 0
    
    # Resolved incidents
    resolved_query = select(func.count(Incident.id)).where(
        Incident.created_at >= start_date,
        Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
    )
    resolved_result = await db.execute(resolved_query)
    resolved = resolved_result.scalar() or 0
    
    # Average resolution time (in minutes)
    avg_resolution_query = select(
        func.avg(
            func.extract('epoch', Incident.resolved_at - Incident.created_at) / 60
        )
    ).where(
        Incident.resolved_at.isnot(None),
        Incident.created_at >= start_date
    )
    avg_resolution_result = await db.execute(avg_resolution_query)
    avg_resolution_time = avg_resolution_result.scalar() or 45.0
    
    # SLA compliance (assuming 4 hour SLA)
    sla_threshold = 240  # 4 hours in minutes
    sla_compliant_query = select(func.count(Incident.id)).where(
        Incident.resolved_at.isnot(None),
        Incident.created_at >= start_date,
        func.extract('epoch', Incident.resolved_at - Incident.created_at) / 60 <= sla_threshold
    )
    sla_compliant_result = await db.execute(sla_compliant_query)
    sla_compliant = sla_compliant_result.scalar() or 0
    
    sla_compliance = (sla_compliant / resolved * 100) if resolved > 0 else 0
    
    return {
        "total_incidents": total_incidents,
        "resolved": resolved,
        "avg_resolution_time_minutes": round(avg_resolution_time, 1),
        "sla_compliance_percentage": round(sla_compliance, 1),
        "period_days": days
    }


@router.get("/incident-trends")
async def get_incident_trends(
    months: int = 6,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get incident trends by month."""
    
    from sqlalchemy import select, func, extract
    
    # Get incidents grouped by month
    query = select(
        extract('year', Incident.created_at).label('year'),
        extract('month', Incident.created_at).label('month'),
        func.count(Incident.id).label('created'),
        func.sum(
            case((Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED]), 1), else_=0)
        ).label('resolved')
    ).where(
        Incident.created_at >= datetime.utcnow() - timedelta(days=months * 30)
    ).group_by(
        extract('year', Incident.created_at),
        extract('month', Incident.created_at)
    ).order_by(
        extract('year', Incident.created_at),
        extract('month', Incident.created_at)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Format results
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    trends = []
    for row in rows:
        month_name = month_names[int(row.month) - 1]
        trends.append({
            "month": month_name,
            "created": row.created or 0,
            "resolved": row.resolved or 0
        })
    
    return trends


@router.get("/alerts-by-severity")
async def get_alerts_by_severity(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get alert distribution by severity."""
    
    from sqlalchemy import select, func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        Alert.severity,
        func.count(Alert.id).label('count')
    ).where(
        Alert.created_at >= start_date
    ).group_by(Alert.severity)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Calculate total for percentages
    total = sum(row.count for row in rows)
    
    severity_data = []
    for row in rows:
        percentage = (row.count / total * 100) if total > 0 else 0
        severity_data.append({
            "severity": row.severity.value.capitalize(),
            "count": row.count,
            "percentage": round(percentage)
        })
    
    return severity_data


@router.get("/top-incident-categories")
async def get_top_incident_categories(
    limit: int = 5,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get top incident categories."""
    
    from sqlalchemy import select, func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        Incident.category,
        func.count(Incident.id).label('count')
    ).where(
        Incident.created_at >= start_date,
        Incident.category.isnot(None)
    ).group_by(Incident.category).order_by(func.count(Incident.id).desc()).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    categories = []
    for row in rows:
        # Mock trend for now (would need historical comparison)
        categories.append({
            "category": row.category or "Uncategorized",
            "count": row.count,
            "trend": 0  # Placeholder
        })
    
    return categories


@router.get("/team-performance")
async def get_team_performance(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get team performance metrics."""
    
    # Mock data for now - would need team assignments and resolution tracking
    return [
        {"team": "Infrastructure", "avgResponse": "8 min", "avgResolution": "45 min", "slaCompliance": 95},
        {"team": "Application", "avgResponse": "12 min", "avgResolution": "1.2 hr", "slaCompliance": 88},
        {"team": "Security", "avgResponse": "5 min", "avgResolution": "2.5 hr", "slaCompliance": 92},
        {"team": "Network", "avgResponse": "15 min", "avgResolution": "35 min", "slaCompliance": 85},
    ]


@router.get("/top-performers")
async def get_top_performers(
    limit: int = 5,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get top performing users."""
    
    from sqlalchemy import select, func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(
        User.id,
        User.first_name,
        User.last_name,
        func.count(Incident.id).label('resolved')
    ).join(
        Incident, Incident.assigned_user_id == User.id
    ).where(
        Incident.resolved_at >= start_date,
        Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
    ).group_by(User.id, User.first_name, User.last_name).order_by(
        func.count(Incident.id).desc()
    ).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    performers = []
    for row in rows:
        performers.append({
            "name": f"{row.first_name} {row.last_name}",
            "resolved": row.resolved,
            "avgTime": "30 min",  # Placeholder
            "rating": 4.5  # Placeholder
        })
    
    return performers


@router.get("/ai-metrics")
async def get_ai_metrics(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI/ML metrics."""
    
    # Mock AI metrics - would be populated by actual AI service usage
    return {
        "incidentsClassified": 156,
        "suggestionsAccepted": 89,
        "predictionsMade": 45,
        "preventedIncidents": 12,
        "accuracyRate": 94.5,
        "timeSaved": "120 hours"
    }


@router.get("/playbook-stats")
async def get_playbook_stats(
    limit: int = 5,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get playbook execution statistics."""
    
    # Mock playbook stats - would come from playbook execution tracking
    return [
        {"name": "Auto-Scale Cluster", "executions": 45, "successRate": 98, "avgDuration": "2.5 min"},
        {"name": "Restart Service", "executions": 38, "successRate": 100, "avgDuration": "1.2 min"},
        {"name": "Clear Cache", "executions": 32, "successRate": 97, "avgDuration": "45 sec"},
        {"name": "Database Backup", "executions": 28, "successRate": 95, "avgDuration": "8 min"},
        {"name": "SSL Renewal", "executions": 15, "successRate": 100, "avgDuration": "3 min"},
    ]

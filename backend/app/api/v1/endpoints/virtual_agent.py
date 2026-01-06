"""
Virtual Agent API endpoints for AI-first Service Desk.

Provides REST API for virtual agent interactions, smart routing,
and proactive support features.
"""

from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import CurrentUser, DBSession
from app.services.virtual_agent_service import VirtualAgentService
from app.services.smart_routing_service import SmartRoutingService
from app.services.proactive_support_service import ProactiveSupportService
from app.models.virtual_agent import Conversation, ConversationStatus
from app.models.user import UserRole

router = APIRouter(prefix="/virtual-agent", tags=["Virtual Agent"])


# Request/Response Models
class StartConversationRequest(BaseModel):
    """Request to start a new conversation."""
    subject: str = Field(..., min_length=1, max_length=500)
    initial_message: str = Field(..., min_length=1, max_length=2000)
    user_email: Optional[str] = None


class SendMessageRequest(BaseModel):
    """Request to send a message in conversation."""
    message: str = Field(..., min_length=1, max_length=2000)


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: str
    subject: str
    status: str
    user_name: str
    intent: Optional[str]
    sentiment: Optional[str]
    category: Optional[str]
    priority: Optional[str]
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Message response."""
    id: str
    type: str
    content: str
    sender_name: Optional[str]
    timestamp: str
    ai_confidence: Optional[float]
    kb_articles: List[str]
    actions: List[str]


class ChatResponse(BaseModel):
    """Chat interaction response."""
    response: str
    confidence: float
    intent: str
    sentiment: str
    category: str
    priority: str
    kb_articles: List[str]
    actions_executed: List[str]
    escalated: bool
    response_time_ms: int


class RoutingRecommendationResponse(BaseModel):
    """Routing recommendation response."""
    recommended_agent: Optional[Dict[str, Any]]
    alternative_agents: List[Dict[str, Any]]
    team_recommendation: Optional[str]
    escalation_needed: bool
    reasoning: str
    confidence: float


class TrendAnalysisResponse(BaseModel):
    """Trend analysis response."""
    trend_type: str
    category: str
    description: str
    confidence: float
    impact_score: int
    recommended_actions: List[str]
    affected_users: int
    time_period: str


class ProactiveRecommendationResponse(BaseModel):
    """Proactive recommendation response."""
    recommendation_id: str
    type: str
    title: str
    description: str
    priority: str
    target_audience: List[str]
    estimated_impact: str
    implementation_effort: str
    success_metrics: List[str]


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection response."""
    anomaly_type: str
    description: str
    severity: str
    affected_area: str
    detection_time: str
    confidence: float
    suggested_investigation: List[str]


# Virtual Agent Endpoints
@router.post("/conversations", response_model=Dict[str, Any])
async def start_conversation(
    request: StartConversationRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Start a new conversation with the virtual agent."""
    
    async with VirtualAgentService(db) as agent_service:
        conversation_id = await agent_service.create_conversation(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            user_name=current_user.full_name,
            user_email=request.user_email or current_user.email,
            subject=request.subject,
            initial_message=request.initial_message
        )
        
        # Get the conversation details
        messages = await agent_service.get_conversation_messages(conversation_id)
        
        return {
            "conversation_id": str(conversation_id),
            "subject": request.subject,
            "status": "active",
            "messages": messages
        }


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: UUID,
    request: SendMessageRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> ChatResponse:
    """Send a message in an existing conversation."""
    
    async with VirtualAgentService(db) as agent_service:
        result = await agent_service.process_message(
            conversation_id=conversation_id,
            message_content=request.message,
            user_id=current_user.id,
            user_name=current_user.full_name
        )
        
        return ChatResponse(**result)


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    limit: int = 50
) -> List[MessageResponse]:
    """Get all messages in a conversation."""
    
    async with VirtualAgentService(db) as agent_service:
        messages = await agent_service.get_conversation_messages(conversation_id, limit)
        
        return [MessageResponse(**msg) for msg in messages]


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: DBSession,
    current_user: CurrentUser,
    status: Optional[str] = None,
    limit: int = 50
) -> List[ConversationResponse]:
    """List user's conversations."""
    
    from sqlalchemy import select, and_
    
    query = select(Conversation).where(
        Conversation.organization_id == current_user.organization_id
    )
    
    # Filter by user if not admin
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        query = query.where(Conversation.user_id == current_user.id)
    
    if status:
        query = query.where(Conversation.status == status)
    
    result = await db.execute(query.limit(limit))
    conversations = result.scalars().all()
    
    return [
        ConversationResponse(
            id=str(conv.id),
            subject=conv.subject,
            status=conv.status,
            user_name=conv.user_name,
            intent=conv.intent,
            sentiment=conv.sentiment,
            category=conv.category,
            priority=conv.priority,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat()
        )
        for conv in conversations
    ]


# Smart Routing Endpoints
@router.post("/routing/tickets/{ticket_id}", response_model=RoutingRecommendationResponse)
async def route_ticket(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    priority_override: Optional[str] = None
) -> RoutingRecommendationResponse:
    """Get routing recommendation for a ticket."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for ticket routing"
        )
    
    async with SmartRoutingService(db) as routing_service:
        recommendation = await routing_service.route_ticket(ticket_id, priority_override)
        
        return RoutingRecommendationResponse(
            recommended_agent={
                "agent_id": str(recommendation.recommended_agent.agent_id),
                "agent_name": recommendation.recommended_agent.agent_name,
                "score": recommendation.recommended_agent.score,
                "reasoning": recommendation.recommended_agent.reasoning,
                "availability": recommendation.recommended_agent.availability,
                "current_workload": recommendation.recommended_agent.current_workload,
                "skill_match": recommendation.recommended_agent.skill_match,
                "performance_score": recommendation.recommended_agent.performance_score
            } if recommendation.recommended_agent else None,
            alternative_agents=[
                {
                    "agent_id": str(agent.agent_id),
                    "agent_name": agent.agent_name,
                    "score": agent.score,
                    "reasoning": agent.reasoning,
                    "availability": agent.availability,
                    "current_workload": agent.current_workload,
                    "skill_match": agent.skill_match,
                    "performance_score": agent.performance_score
                }
                for agent in recommendation.alternative_agents
            ],
            team_recommendation=recommendation.team_recommendation,
            escalation_needed=recommendation.escalation_needed,
            reasoning=recommendation.reasoning,
            confidence=recommendation.confidence
        )


@router.post("/routing/conversations/{conversation_id}", response_model=RoutingRecommendationResponse)
async def route_conversation(
    conversation_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> RoutingRecommendationResponse:
    """Get routing recommendation for an escalated conversation."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for conversation routing"
        )
    
    async with SmartRoutingService(db) as routing_service:
        recommendation = await routing_service.route_conversation(conversation_id)
        
        return RoutingRecommendationResponse(
            recommended_agent={
                "agent_id": str(recommendation.recommended_agent.agent_id),
                "agent_name": recommendation.recommended_agent.agent_name,
                "score": recommendation.recommended_agent.score,
                "reasoning": recommendation.recommended_agent.reasoning,
                "availability": recommendation.recommended_agent.availability,
                "current_workload": recommendation.recommended_agent.current_workload,
                "skill_match": recommendation.recommended_agent.skill_match,
                "performance_score": recommendation.recommended_agent.performance_score
            } if recommendation.recommended_agent else None,
            alternative_agents=[
                {
                    "agent_id": str(agent.agent_id),
                    "agent_name": agent.agent_name,
                    "score": agent.score,
                    "reasoning": agent.reasoning,
                    "availability": agent.availability,
                    "current_workload": agent.current_workload,
                    "skill_match": agent.skill_match,
                    "performance_score": agent.performance_score
                }
                for agent in recommendation.alternative_agents
            ],
            team_recommendation=recommendation.team_recommendation,
            escalation_needed=recommendation.escalation_needed,
            reasoning=recommendation.reasoning,
            confidence=recommendation.confidence
        )


@router.post("/routing/assign/{ticket_id}")
async def assign_ticket(
    ticket_id: UUID,
    agent_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Assign a ticket to an agent."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for ticket assignment"
        )
    
    async with SmartRoutingService(db) as routing_service:
        success = await routing_service.assign_ticket(
            ticket_id=ticket_id,
            agent_id=agent_id,
            assigned_by_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign ticket"
            )
        
        return {"success": True, "message": "Ticket assigned successfully"}


# Proactive Support Endpoints
@router.get("/analytics/trends", response_model=List[TrendAnalysisResponse])
async def analyze_support_trends(
    db: DBSession,
    current_user: CurrentUser,
    days_back: int = 30
) -> List[TrendAnalysisResponse]:
    """Analyze support trends and patterns."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for analytics"
        )
    
    async with ProactiveSupportService(db) as proactive_service:
        trends = await proactive_service.analyze_support_trends(
            current_user.organization_id,
            days_back
        )
        
        return [
            TrendAnalysisResponse(
                trend_type=trend.trend_type,
                category=trend.category,
                description=trend.description,
                confidence=trend.confidence,
                impact_score=trend.impact_score,
                recommended_actions=trend.recommended_actions,
                affected_users=trend.affected_users,
                time_period=trend.time_period
            )
            for trend in trends
        ]


@router.get("/analytics/anomalies", response_model=List[AnomalyDetectionResponse])
async def detect_anomalies(
    db: DBSession,
    current_user: CurrentUser,
    hours_back: int = 24
) -> List[AnomalyDetectionResponse]:
    """Detect anomalies in support metrics."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for anomaly detection"
        )
    
    async with ProactiveSupportService(db) as proactive_service:
        anomalies = await proactive_service.detect_anomalies(
            current_user.organization_id,
            hours_back
        )
        
        return [
            AnomalyDetectionResponse(
                anomaly_type=anomaly.anomaly_type,
                description=anomaly.description,
                severity=anomaly.severity,
                affected_area=anomaly.affected_area,
                detection_time=anomaly.detection_time.isoformat(),
                confidence=anomaly.confidence,
                suggested_investigation=anomaly.suggested_investigation
            )
            for anomaly in anomalies
        ]


@router.get("/analytics/recommendations", response_model=List[ProactiveRecommendationResponse])
async def get_proactive_recommendations(
    db: DBSession,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
) -> List[ProactiveRecommendationResponse]:
    """Get proactive support recommendations."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for recommendations"
        )
    
    async with ProactiveSupportService(db) as proactive_service:
        # Get trends and anomalies
        trends = await proactive_service.analyze_support_trends(current_user.organization_id)
        anomalies = await proactive_service.detect_anomalies(current_user.organization_id)
        
        # Generate recommendations
        recommendations = await proactive_service.generate_proactive_recommendations(
            current_user.organization_id,
            trends,
            anomalies
        )
        
        return [
            ProactiveRecommendationResponse(
                recommendation_id=rec.recommendation_id,
                type=rec.type,
                title=rec.title,
                description=rec.description,
                priority=rec.priority,
                target_audience=rec.target_audience,
                estimated_impact=rec.estimated_impact,
                implementation_effort=rec.implementation_effort,
                success_metrics=rec.success_metrics
            )
            for rec in recommendations
        ]


@router.get("/analytics/knowledge-gaps")
async def identify_knowledge_gaps(
    db: DBSession,
    current_user: CurrentUser,
    days_back: int = 30
) -> List[Dict[str, Any]]:
    """Identify gaps in knowledge base coverage."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for knowledge gap analysis"
        )
    
    async with ProactiveSupportService(db) as proactive_service:
        gaps = await proactive_service.identify_knowledge_gaps(
            current_user.organization_id,
            days_back
        )
        
        return gaps


# Agent Performance Endpoints
@router.get("/performance/agents")
async def get_agent_performance(
    db: DBSession,
    current_user: CurrentUser,
    days_back: int = 30
) -> List[Dict[str, Any]]:
    """Get agent performance metrics."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required for performance metrics"
        )
    
    from sqlalchemy import select, and_, func
    from app.models.virtual_agent import AgentPerformance
    from datetime import datetime, timezone, timedelta
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    # Get agent performance data
    result = await db.execute(
        select(
            AgentPerformance.agent_id,
            func.avg(AgentPerformance.avg_resolution_time_minutes).label("avg_resolution_time"),
            func.avg(AgentPerformance.customer_satisfaction_avg).label("avg_satisfaction"),
            func.avg(AgentPerformance.first_contact_resolution_rate).label("avg_fcr_rate"),
            func.sum(AgentPerformance.tickets_handled).label("total_tickets"),
            func.sum(AgentPerformance.conversations_handled).label("total_conversations")
        ).where(
            and_(
                AgentPerformance.organization_id == current_user.organization_id,
                AgentPerformance.date >= start_date
            )
        ).group_by(AgentPerformance.agent_id)
    )
    
    performance_data = result.fetchall()
    
    # Get agent names
    from app.models.user import User
    agent_ids = [row.agent_id for row in performance_data]
    
    if agent_ids:
        agents_result = await db.execute(
            select(User).where(User.id.in_(agent_ids))
        )
        agents = {agent.id: agent.full_name for agent in agents_result.scalars().all()}
    else:
        agents = {}
    
    return [
        {
            "agent_id": str(row.agent_id),
            "agent_name": agents.get(row.agent_id, "Unknown"),
            "avg_resolution_time_minutes": float(row.avg_resolution_time or 0),
            "avg_satisfaction": float(row.avg_satisfaction or 0),
            "avg_fcr_rate": float(row.avg_fcr_rate or 0),
            "total_tickets": int(row.total_tickets or 0),
            "total_conversations": int(row.total_conversations or 0)
        }
        for row in performance_data
    ]


@router.get("/status")
async def get_virtual_agent_status(
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Get virtual agent system status."""
    
    from sqlalchemy import select, func, and_
    from datetime import datetime, timezone, timedelta
    
    # Get recent statistics
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    
    # Conversation stats
    conv_result = await db.execute(
        select(
            func.count(Conversation.id).label("total_conversations"),
            func.sum(
                func.case(
                    (Conversation.resolution_type == "virtual_agent", 1),
                    else_=0
                )
            ).label("auto_resolved"),
            func.avg(Conversation.confidence).label("avg_confidence")
        ).where(
            and_(
                Conversation.organization_id == current_user.organization_id,
                Conversation.created_at >= last_24h
            )
        )
    )
    
    conv_stats = conv_result.fetchone()
    
    total_conversations = int(conv_stats.total_conversations or 0)
    auto_resolved = int(conv_stats.auto_resolved or 0)
    auto_resolution_rate = (auto_resolved / total_conversations) if total_conversations > 0 else 0
    avg_confidence = float(conv_stats.avg_confidence or 0)
    
    return {
        "status": "active",
        "last_24h_stats": {
            "total_conversations": total_conversations,
            "auto_resolved": auto_resolved,
            "auto_resolution_rate": auto_resolution_rate,
            "avg_confidence": avg_confidence
        },
        "ai_enabled": bool(settings.ANTHROPIC_API_KEY),
        "features": {
            "intent_recognition": True,
            "smart_routing": True,
            "proactive_support": True,
            "knowledge_integration": True
        }
    }
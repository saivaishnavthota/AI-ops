import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select, update, delete, func
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.api.v1.deps import CurrentUser, DBSession
from app.models import Ticket, KnowledgeBaseArticle, User
from app.models.user import UserRole
from app.models.team import Team, TeamMember
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    KnowledgeBaseArticleCreate,
    KnowledgeBaseArticleUpdate,
    KnowledgeBaseArticleResponse,
    KnowledgeBaseArticleListResponse,
)
from app.services.virtual_agent_service import VirtualAgentService
from app.services.smart_routing_service import SmartRoutingService
from app.services.proactive_support_service import ProactiveSupportService
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService
from app.core.audit_logger import log_create, log_update, log_delete, log_assign, log_resolve

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["Service Desk"])
kb_router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])
users_router = APIRouter(prefix="/users", tags=["Users"])


# User endpoints for ticket assignment
@users_router.get("/assignable", response_model=List[Dict[str, Any]])
async def get_assignable_users(
    db: DBSession,
    current_user: CurrentUser,
):
    """Get list of users who can be assigned tickets (operators and admins)."""
    
    # Get all active users with operator or admin roles
    result = await db.execute(
        select(User).where(
            User.organization_id == current_user.organization_id,
            User.is_active == True,
            User.role.in_([UserRole.OPERATOR.value, UserRole.ADMIN.value])
        ).order_by(User.first_name, User.last_name)
    )
    users = result.scalars().all()
    
    # Get team memberships for each user
    team_memberships_result = await db.execute(
        select(TeamMember, Team).join(Team).where(
            TeamMember.user_id.in_([user.id for user in users])
        )
    )
    team_memberships = team_memberships_result.all()
    
    # Create user data with team information
    assignable_users = []
    for user in users:
        # Find user's teams
        user_teams = []
        for membership, team in team_memberships:
            if membership.user_id == user.id:
                user_teams.append({
                    "team_name": team.name,
                    "team_type": team.team_type,
                    "role": membership.role
                })
        
        assignable_users.append({
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "job_title": user.job_title,
            "teams": user_teams,
            "display_name": f"{user.full_name} ({user.job_title or user.role})"
        })
    
    return assignable_users


# Ticket endpoints
@router.get("", response_model=TicketListResponse)
async def list_tickets(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_only: bool = Query(False, description="Show only tickets assigned to current user"),
):
    """List tickets for the organization. Operators see only assigned tickets by default."""
    query = select(Ticket).where(
        Ticket.organization_id == current_user.organization_id
    )
    
    # For operators, show only assigned tickets by default (unless admin overrides)
    if current_user.role == UserRole.OPERATOR.value and not current_user.role == UserRole.ADMIN.value:
        query = query.where(Ticket.assignee_id == current_user.id)
    elif assigned_only:
        query = query.where(Ticket.assignee_id == current_user.id)
    
    # Exclude tickets that should be moved to incidents (resolved > 1 day ago)
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    query = query.where(
        (Ticket.status != "resolved") | 
        (Ticket.resolved_at.is_(None)) |
        (Ticket.resolved_at > one_day_ago)
    )
    
    if status:
        query = query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
    
    # Get total count with same filters
    count_query = select(func.count(Ticket.id)).where(
        Ticket.organization_id == current_user.organization_id
    )
    
    if current_user.role == UserRole.OPERATOR.value and not current_user.role == UserRole.ADMIN.value:
        count_query = count_query.where(Ticket.assignee_id == current_user.id)
    elif assigned_only:
        count_query = count_query.where(Ticket.assignee_id == current_user.id)
        
    count_query = count_query.where(
        (Ticket.status != "resolved") | 
        (Ticket.resolved_at.is_(None)) |
        (Ticket.resolved_at > one_day_ago)
    )
    
    if status:
        count_query = count_query.where(Ticket.status == status)
    if priority:
        count_query = count_query.where(Ticket.priority == priority)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # Get tickets with pagination
    result = await db.execute(
        query.order_by(desc(Ticket.created_at)).offset(skip).limit(limit)
    )
    tickets = result.scalars().all()
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": tickets,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    db: DBSession,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    request: Request,
    auto_classify: bool = Query(True, description="Enable AI auto-classification"),
    auto_route: bool = Query(True, description="Enable AI auto-routing"),
):
    """Create a new ticket with AI enhancements."""
    ticket = Ticket(
        organization_id=current_user.organization_id,
        requester_id=current_user.id,
        requester_name=current_user.full_name,
        status="open",
        comments=[],
        **ticket_in.dict(),
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    # Audit log
    await log_create(
        db=db,
        user=current_user,
        resource_type="ticket",
        resource_id=str(ticket.id),
        resource_name=ticket.subject,
        request=request,
    )
    
    # AI Enhancement: Auto-classify and route ticket
    if auto_classify or auto_route:
        background_tasks.add_task(
            _enhance_ticket_with_ai,
            ticket.id,
            current_user.organization_id,
            auto_classify,
            auto_route
        )
    
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific ticket."""
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: UUID,
    ticket_in: TicketUpdate,
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Update a ticket."""
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    update_data = ticket_in.dict(exclude_unset=True)
    
    # If resolving, set resolved_at
    if update_data.get("status") == "resolved" and ticket.status != "resolved":
        update_data["resolved_at"] = datetime.now(timezone.utc)
    
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    await db.commit()
    await db.refresh(ticket)
    
    # Audit log
    await log_update(
        db=db,
        user=current_user,
        resource_type="ticket",
        resource_id=str(ticket.id),
        resource_name=ticket.subject,
        request=request,
    )
    
    return ticket


@router.put("/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_ticket_with_feedback(
    ticket_id: UUID,
    feedback_data: Dict[str, Any],
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Resolve a ticket and create knowledge base article from feedback."""
    
    # Get the ticket
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Check if user can resolve this ticket (assigned to them or admin)
    if (ticket.assignee_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only resolve tickets assigned to you",
        )
    
    # Update ticket status
    ticket.status = "resolved"
    ticket.resolved_at = datetime.now(timezone.utc)
    
    # Add resolution comment
    resolution_comment = {
        "user": current_user.full_name,
        "text": f"Ticket resolved by {current_user.full_name}",
        "time": datetime.now(timezone.utc).isoformat(),
        "resolution": True
    }
    
    if not ticket.comments:
        ticket.comments = []
    ticket.comments.append(resolution_comment)
    
    # Create knowledge base article from feedback if provided
    feedback_title = feedback_data.get("title", "")
    feedback_content = feedback_data.get("content", "")
    feedback_tags = feedback_data.get("tags", [])
    
    if feedback_title and feedback_content:
        # Create knowledge base article
        kb_article = KnowledgeBaseArticle(
            organization_id=current_user.organization_id,
            author_id=current_user.id,
            title=feedback_title,
            content=feedback_content,
            excerpt=feedback_content[:200] + "..." if len(feedback_content) > 200 else feedback_content,
            category=ticket.category,
            tags=feedback_tags,
            views=0,
            helpful_count=0,
            is_published=True,
        )
        db.add(kb_article)
        
        # Add feedback comment to ticket
        feedback_comment = {
            "user": current_user.full_name,
            "text": f"Knowledge shared: Created KB article '{feedback_title}'",
            "time": datetime.now(timezone.utc).isoformat(),
            "knowledge_shared": True,
            "kb_article_id": str(kb_article.id)
        }
        ticket.comments.append(feedback_comment)
    
    await db.commit()
    await db.refresh(ticket)
    
    # Audit log
    await log_resolve(
        db=db,
        user=current_user,
        resource_type="ticket",
        resource_id=str(ticket.id),
        resource_name=ticket.subject,
        request=request,
    )
    
    return ticket


@router.get("/resolved-old", response_model=TicketListResponse)
async def get_old_resolved_tickets(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get resolved tickets older than 1 day (should be moved to incidents)."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    
    query = select(Ticket).where(
        Ticket.organization_id == current_user.organization_id,
        Ticket.status == "resolved",
        Ticket.resolved_at <= one_day_ago
    )
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.organization_id == current_user.organization_id,
            Ticket.status == "resolved",
            Ticket.resolved_at <= one_day_ago
        )
    )
    total = count_result.scalar()
    
    # Get tickets with pagination
    result = await db.execute(
        query.order_by(desc(Ticket.resolved_at)).offset(skip).limit(limit)
    )
    tickets = result.scalars().all()
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit
    
    return {
        "items": tickets,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@router.put("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket_to_user(
    ticket_id: UUID,
    assignment_data: Dict[str, Any],
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Assign a ticket to a specific user."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign tickets",
        )
    
    # Get the ticket
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Get the assignee user
    assignee_id = assignment_data.get("assignee_id")
    if not assignee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignee ID is required",
        )
    
    assignee_result = await db.execute(
        select(User).where(
            User.id == assignee_id,
            User.organization_id == current_user.organization_id,
            User.is_active == True,
            User.role.in_([UserRole.OPERATOR.value, UserRole.ADMIN.value])
        )
    )
    assignee = assignee_result.scalar_one_or_none()
    
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found or not eligible for ticket assignment",
        )
    
    # Update ticket assignment
    old_assignee = ticket.assignee_name
    ticket.assignee_id = assignee.id
    ticket.assignee_name = assignee.full_name
    ticket.status = "in_progress"  # Change status when assigned
    
    # Add assignment comment
    assignment_comment = {
        "user": current_user.full_name,
        "text": f"Ticket assigned to {assignee.full_name}" + (f" (previously: {old_assignee})" if old_assignee else ""),
        "time": datetime.now(timezone.utc).isoformat(),
        "assignment": True,
        "assigned_by": current_user.full_name,
        "assigned_to": assignee.full_name
    }
    
    if not ticket.comments:
        ticket.comments = []
    ticket.comments.append(assignment_comment)
    
    await db.commit()
    await db.refresh(ticket)
    
    # Create notification for the assignee
    notification_service = NotificationService(db)
    await notification_service.notify_ticket_assignment(
        ticket=ticket,
        assignee=assignee,
        assigned_by=current_user,
    )
    
    # Audit log
    await log_assign(
        db=db,
        user=current_user,
        resource_type="ticket",
        resource_id=str(ticket.id),
        resource_name=ticket.subject,
        assigned_to=assignee.full_name,
        request=request,
    )
    
    return ticket


@router.post("/migrate-to-incidents")
async def migrate_old_tickets_to_incidents(
    db: DBSession,
    current_user: CurrentUser,
):
    """Manually trigger migration of old resolved tickets to incidents."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    try:
        # Import the migration function
        from ..tasks.ticket_migration import migrate_old_resolved_tickets
        
        migrated_count = await migrate_old_resolved_tickets()
        
        return {
            "success": True,
            "migrated_count": migrated_count,
            "message": f"Successfully migrated {migrated_count} resolved tickets to incidents"
        }
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    request: Request,
):
    """Delete a ticket."""
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    ticket_subject = ticket.subject
    await db.execute(delete(Ticket).where(Ticket.id == ticket_id))
    await db.commit()
    
    # Audit log
    await log_delete(
        db=db,
        user=current_user,
        resource_type="ticket",
        resource_id=str(ticket_id),
        resource_name=ticket_subject,
        request=request,
    )


@router.get("/resolved-old", response_model=TicketListResponse)
async def get_old_resolved_tickets(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Get resolved tickets older than 1 day (should be moved to incidents)."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    
    query = select(Ticket).where(
        Ticket.organization_id == current_user.organization_id,
        Ticket.status == "resolved",
        Ticket.resolved_at <= one_day_ago
    )
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Ticket.id)).where(
            Ticket.organization_id == current_user.organization_id,
            Ticket.status == "resolved",
            Ticket.resolved_at <= one_day_ago
        )
    )
    total = count_result.scalar()
    
    # Get tickets with pagination
    result = await db.execute(
        query.order_by(desc(Ticket.resolved_at)).offset(skip).limit(limit)
    )
    tickets = result.scalars().all()
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit
    
    return {
        "items": tickets,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }
async def delete_ticket(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Delete a ticket."""
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    await db.execute(delete(Ticket).where(Ticket.id == ticket_id))
    await db.commit()


# Knowledge Base endpoints
@kb_router.get("", response_model=KnowledgeBaseArticleListResponse)
async def list_kb_articles(
    db: DBSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """List all knowledge base articles."""
    query = select(KnowledgeBaseArticle).where(
        KnowledgeBaseArticle.organization_id == current_user.organization_id,
        KnowledgeBaseArticle.is_published == True,
    )
    
    if category:
        query = query.where(KnowledgeBaseArticle.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (KnowledgeBaseArticle.title.ilike(search_term)) |
            (KnowledgeBaseArticle.excerpt.ilike(search_term)) |
            (KnowledgeBaseArticle.content.ilike(search_term))
        )
    
    # Get total count
    count_result = await db.execute(
        select(func.count(KnowledgeBaseArticle.id)).where(
            KnowledgeBaseArticle.organization_id == current_user.organization_id,
            KnowledgeBaseArticle.is_published == True,
        )
    )
    total = count_result.scalar()
    
    # Get articles with pagination
    result = await db.execute(
        query.order_by(desc(KnowledgeBaseArticle.updated_at)).offset(skip).limit(limit)
    )
    articles = result.scalars().all()
    
    # Calculate pagination fields
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "items": articles,
        "total": total,
        "page": page,
        "page_size": limit,
        "pages": pages,
    }


@kb_router.post("", response_model=KnowledgeBaseArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_kb_article(
    article_in: KnowledgeBaseArticleCreate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Create a new knowledge base article."""
    article = KnowledgeBaseArticle(
        organization_id=current_user.organization_id,
        author_id=current_user.id,
        views=0,
        helpful_count=0,
        is_published=True,
        **article_in.dict(),
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


@kb_router.get("/{article_id}", response_model=KnowledgeBaseArticleResponse)
async def get_kb_article(
    article_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Get a specific knowledge base article."""
    result = await db.execute(
        select(KnowledgeBaseArticle).where(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.organization_id == current_user.organization_id,
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    
    # Increment views
    article.views += 1
    await db.commit()
    await db.refresh(article)
    
    return article


@kb_router.put("/{article_id}", response_model=KnowledgeBaseArticleResponse)
async def update_kb_article(
    article_id: UUID,
    article_in: KnowledgeBaseArticleUpdate,
    db: DBSession,
    current_user: CurrentUser,
):
    """Update a knowledge base article."""
    result = await db.execute(
        select(KnowledgeBaseArticle).where(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.organization_id == current_user.organization_id,
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    
    update_data = article_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)
    
    await db.commit()
    await db.refresh(article)
    return article


@kb_router.post("/{article_id}/helpful", response_model=KnowledgeBaseArticleResponse)
async def mark_article_helpful(
    article_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Mark an article as helpful."""
    result = await db.execute(
        select(KnowledgeBaseArticle).where(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.organization_id == current_user.organization_id,
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    
    article.helpful_count += 1
    await db.commit()
    await db.refresh(article)
    return article


@kb_router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kb_article(
    article_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """Delete a knowledge base article."""
    result = await db.execute(
        select(KnowledgeBaseArticle).where(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.organization_id == current_user.organization_id,
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    
    await db.execute(delete(KnowledgeBaseArticle).where(KnowledgeBaseArticle.id == article_id))
    await db.commit()


# AI-Enhanced Service Desk Endpoints

@router.post("/{ticket_id}/ai-classify")
async def classify_ticket_with_ai(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Classify ticket using AI and update with suggestions."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for AI classification"
        )
    
    # Get ticket
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    async with VirtualAgentService(db) as agent_service:
        # Analyze ticket intent and category
        intent_result = await agent_service._analyze_intent(
            f"{ticket.subject}. {ticket.description}",
            current_user.organization_id
        )
        
        # Find relevant KB articles
        kb_articles = await agent_service._find_relevant_kb_articles(
            intent_result.keywords,
            intent_result.category,
            current_user.organization_id
        )
        
        # Update ticket with AI insights
        if not ticket.comments:
            ticket.comments = []
        
        ai_comment = {
            "user": "AI Assistant",
            "text": f"AI Classification: Category: {intent_result.category}, Intent: {intent_result.intent}, Priority: {intent_result.priority}, Confidence: {intent_result.confidence:.1%}",
            "time": datetime.now(timezone.utc).isoformat(),
            "ai_analysis": {
                "intent": intent_result.intent,
                "category": intent_result.category,
                "priority": intent_result.priority,
                "confidence": intent_result.confidence,
                "keywords": intent_result.keywords,
                "suggested_actions": intent_result.suggested_actions,
                "kb_articles": [{"id": str(article["id"]), "title": article["title"]} for article in kb_articles]
            }
        }
        
        ticket.comments.append(ai_comment)
        
        # Update category if not set or low confidence
        if not ticket.category or intent_result.confidence > 0.8:
            ticket.category = intent_result.category
        
        await db.commit()
        await db.refresh(ticket)
        
        return {
            "ticket_id": str(ticket_id),
            "ai_analysis": ai_comment["ai_analysis"],
            "kb_articles_found": len(kb_articles),
            "updated": True
        }


@router.post("/{ticket_id}/ai-route")
async def route_ticket_with_ai(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Get AI routing recommendations for ticket."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for AI routing"
        )
    
    async with SmartRoutingService(db) as routing_service:
        recommendation = await routing_service.route_ticket(ticket_id)
        
        return {
            "ticket_id": str(ticket_id),
            "recommended_agent": {
                "agent_id": str(recommendation.recommended_agent.agent_id),
                "agent_name": recommendation.recommended_agent.agent_name,
                "score": recommendation.recommended_agent.score,
                "reasoning": recommendation.recommended_agent.reasoning,
                "availability": recommendation.recommended_agent.availability,
                "current_workload": recommendation.recommended_agent.current_workload
            } if recommendation.recommended_agent else None,
            "alternative_agents": [
                {
                    "agent_id": str(agent.agent_id),
                    "agent_name": agent.agent_name,
                    "score": agent.score,
                    "availability": agent.availability,
                    "current_workload": agent.current_workload
                }
                for agent in recommendation.alternative_agents[:3]  # Top 3 alternatives
            ],
            "team_recommendation": recommendation.team_recommendation,
            "escalation_needed": recommendation.escalation_needed,
            "reasoning": recommendation.reasoning,
            "confidence": recommendation.confidence
        }


@router.post("/{ticket_id}/ai-assign/{agent_id}")
async def assign_ticket_with_ai(
    ticket_id: UUID,
    agent_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Assign ticket to agent using AI routing."""
    
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
        
        return {
            "success": True,
            "message": "Ticket assigned successfully using AI routing",
            "ticket_id": str(ticket_id),
            "agent_id": str(agent_id)
        }


@router.get("/ai-analytics/trends")
async def get_ticket_trends(
    db: DBSession,
    current_user: CurrentUser,
    days_back: int = Query(30, ge=1, le=90),
) -> Dict[str, Any]:
    """Get AI-powered ticket trend analysis."""
    
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
        
        return {
            "organization_id": str(current_user.organization_id),
            "analysis_period_days": days_back,
            "trends": [
                {
                    "trend_type": trend.trend_type,
                    "category": trend.category,
                    "description": trend.description,
                    "confidence": trend.confidence,
                    "impact_score": trend.impact_score,
                    "recommended_actions": trend.recommended_actions,
                    "affected_users": trend.affected_users,
                    "time_period": trend.time_period
                }
                for trend in trends
            ],
            "total_trends": len(trends),
            "high_impact_trends": len([t for t in trends if t.impact_score >= 7])
        }


@router.get("/ai-analytics/anomalies")
async def detect_ticket_anomalies(
    db: DBSession,
    current_user: CurrentUser,
    hours_back: int = Query(24, ge=1, le=168),
) -> Dict[str, Any]:
    """Detect anomalies in ticket patterns."""
    
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
        
        return {
            "organization_id": str(current_user.organization_id),
            "analysis_period_hours": hours_back,
            "anomalies": [
                {
                    "anomaly_type": anomaly.anomaly_type,
                    "description": anomaly.description,
                    "severity": anomaly.severity,
                    "affected_area": anomaly.affected_area,
                    "detection_time": anomaly.detection_time.isoformat(),
                    "confidence": anomaly.confidence,
                    "suggested_investigation": anomaly.suggested_investigation
                }
                for anomaly in anomalies
            ],
            "total_anomalies": len(anomalies),
            "critical_anomalies": len([a for a in anomalies if a.severity == "high"])
        }


@router.get("/ai-analytics/recommendations")
async def get_proactive_recommendations(
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Get AI-powered proactive support recommendations."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for recommendations"
        )
    
    async with ProactiveSupportService(db) as proactive_service:
        # Get trends and anomalies first
        trends = await proactive_service.analyze_support_trends(current_user.organization_id)
        anomalies = await proactive_service.detect_anomalies(current_user.organization_id)
        
        # Generate recommendations
        recommendations = await proactive_service.generate_proactive_recommendations(
            current_user.organization_id,
            trends,
            anomalies
        )
        
        return {
            "organization_id": str(current_user.organization_id),
            "recommendations": [
                {
                    "recommendation_id": rec.recommendation_id,
                    "type": rec.type,
                    "title": rec.title,
                    "description": rec.description,
                    "priority": rec.priority,
                    "target_audience": rec.target_audience,
                    "estimated_impact": rec.estimated_impact,
                    "implementation_effort": rec.implementation_effort,
                    "success_metrics": rec.success_metrics
                }
                for rec in recommendations
            ],
            "total_recommendations": len(recommendations),
            "high_priority_recommendations": len([r for r in recommendations if r.priority == "high"])
        }


# Knowledge Base AI Enhancements

@kb_router.get("/ai-analytics/gaps")
async def identify_knowledge_gaps(
    db: DBSession,
    current_user: CurrentUser,
    days_back: int = Query(30, ge=1, le=90),
) -> Dict[str, Any]:
    """Identify gaps in knowledge base coverage using AI analysis."""
    
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
        
        return {
            "organization_id": str(current_user.organization_id),
            "analysis_period_days": days_back,
            "knowledge_gaps": gaps,
            "total_gaps": len(gaps),
            "high_priority_gaps": len([g for g in gaps if g.get("priority") == "high"]),
            "recommended_articles": sum(g.get("recommended_articles", 0) for g in gaps)
        }


@kb_router.post("/{article_id}/ai-enhance")
async def enhance_kb_article_with_ai(
    article_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> Dict[str, Any]:
    """Enhance knowledge base article with AI suggestions."""
    
    # Check permissions
    if current_user.role not in [UserRole.ADMIN.value, UserRole.OPERATOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for AI enhancement"
        )
    
    # Get article
    result = await db.execute(
        select(KnowledgeBaseArticle).where(
            KnowledgeBaseArticle.id == article_id,
            KnowledgeBaseArticle.organization_id == current_user.organization_id,
        )
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    
    async with VirtualAgentService(db) as agent_service:
        # Analyze article content and suggest improvements
        intent_result = await agent_service._analyze_intent(
            f"{article.title}. {article.content}",
            current_user.organization_id
        )
        
        # Find related tickets to understand common issues
        related_tickets_result = await db.execute(
            select(Ticket).where(
                Ticket.organization_id == current_user.organization_id,
                Ticket.category == article.category
            ).order_by(desc(Ticket.created_at)).limit(10)
        )
        related_tickets = related_tickets_result.scalars().all()
        
        # Generate enhancement suggestions
        suggestions = {
            "content_analysis": {
                "category": intent_result.category,
                "keywords": intent_result.keywords,
                "confidence": intent_result.confidence
            },
            "related_tickets_count": len(related_tickets),
            "common_issues": [
                {
                    "subject": ticket.subject,
                    "category": ticket.category,
                    "priority": ticket.priority
                }
                for ticket in related_tickets[:5]
            ],
            "enhancement_suggestions": [
                "Add more specific troubleshooting steps",
                "Include common error messages and solutions",
                "Add screenshots or diagrams if applicable",
                "Include links to related articles",
                "Add FAQ section for common questions"
            ],
            "seo_keywords": intent_result.keywords,
            "effectiveness_score": min(100, (article.helpful_count / max(1, article.views)) * 100)
        }
        
        return {
            "article_id": str(article_id),
            "current_stats": {
                "views": article.views,
                "helpful_count": article.helpful_count,
                "effectiveness_rate": suggestions["effectiveness_score"]
            },
            "ai_suggestions": suggestions
        }


@router.get("/{ticket_id}/related-articles", response_model=List[Dict[str, Any]])
async def get_related_kb_articles(
    ticket_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    limit: int = Query(5, ge=1, le=10, description="Maximum number of related articles to return"),
):
    """Get AI-recommended related KB articles for a ticket based on content similarity."""
    
    # Get the ticket
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.organization_id == current_user.organization_id,
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    try:
        # Extract keywords from ticket (simple approach)
        ticket_text = f"{ticket.subject} {ticket.description}".lower()
        
        # Simple keyword extraction - split and filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
        words = [w.strip('.,!?;:()[]{}') for w in ticket_text.split()]
        keywords = [w for w in words if len(w) > 3 and w not in stop_words][:10]
        
        # Search for related KB articles
        from sqlalchemy import or_, and_
        
        # Build search query with keywords and category
        search_conditions = []
        
        # Add keyword searches
        for keyword in keywords[:5]:  # Use top 5 keywords
            search_conditions.append(KnowledgeBaseArticle.title.ilike(f"%{keyword}%"))
            search_conditions.append(KnowledgeBaseArticle.content.ilike(f"%{keyword}%"))
            search_conditions.append(KnowledgeBaseArticle.excerpt.ilike(f"%{keyword}%"))
        
        # Add category match (higher priority)
        search_conditions.append(KnowledgeBaseArticle.category == ticket.category)
        
        # Query KB articles
        if search_conditions:
            kb_result = await db.execute(
                select(KnowledgeBaseArticle).where(
                    and_(
                        KnowledgeBaseArticle.organization_id == current_user.organization_id,
                        KnowledgeBaseArticle.is_published == True,
                        or_(*search_conditions)
                    )
                ).order_by(
                    desc(KnowledgeBaseArticle.helpful_count),
                    desc(KnowledgeBaseArticle.views)
                ).limit(limit)
            )
            
            articles = kb_result.scalars().all()
        else:
            # If no keywords, just return articles from same category
            kb_result = await db.execute(
                select(KnowledgeBaseArticle).where(
                    and_(
                        KnowledgeBaseArticle.organization_id == current_user.organization_id,
                        KnowledgeBaseArticle.is_published == True,
                        KnowledgeBaseArticle.category == ticket.category
                    )
                ).order_by(
                    desc(KnowledgeBaseArticle.helpful_count),
                    desc(KnowledgeBaseArticle.views)
                ).limit(limit)
            )
            articles = kb_result.scalars().all()
        
        # Format response
        related_articles = []
        for article in articles:
            # Calculate simple relevance score based on keyword matches
            relevance = 0.5  # Base score for category match
            article_text = f"{article.title} {article.excerpt}".lower()
            matches = sum(1 for kw in keywords[:5] if kw in article_text)
            relevance += (matches / 5) * 0.5  # Add up to 0.5 for keyword matches
            
            related_articles.append({
                "id": str(article.id),
                "title": article.title,
                "excerpt": article.excerpt,
                "category": article.category,
                "tags": article.tags,
                "views": article.views,
                "helpful_count": article.helpful_count,
                "relevance_score": min(relevance, 1.0),
            })
        
        # Sort by relevance score
        related_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return related_articles
        
    except Exception as e:
        logger.error(f"Error finding related KB articles: {e}")
        # Return empty list on error rather than failing
        return []


# Helper function for background AI processing
async def _enhance_ticket_with_ai(
    ticket_id: UUID,
    organization_id: UUID,
    auto_classify: bool,
    auto_route: bool
):
    """Background task to enhance ticket with AI."""
    from app.config.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Get ticket
            result = await db.execute(
                select(Ticket).where(Ticket.id == ticket_id)
            )
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return
            
            if auto_classify:
                async with VirtualAgentService(db) as agent_service:
                    # Analyze and classify
                    intent_result = await agent_service._analyze_intent(
                        f"{ticket.subject}. {ticket.description}",
                        organization_id
                    )
                    
                    # Update ticket category if confidence is high
                    if intent_result.confidence > 0.7:
                        ticket.category = intent_result.category
                        
                        # Add AI comment
                        if not ticket.comments:
                            ticket.comments = []
                        
                        ai_comment = {
                            "user": "AI Assistant",
                            "text": f"Auto-classified as {intent_result.category} (confidence: {intent_result.confidence:.1%})",
                            "time": datetime.now(timezone.utc).isoformat(),
                            "ai_classification": {
                                "intent": intent_result.intent,
                                "category": intent_result.category,
                                "confidence": intent_result.confidence,
                                "keywords": intent_result.keywords
                            }
                        }
                        ticket.comments.append(ai_comment)
            
            if auto_route:
                async with SmartRoutingService(db) as routing_service:
                    # Get ticket object first
                    ticket_update = await db.execute(
                        select(Ticket).where(Ticket.id == ticket_id)
                    )
                    ticket_obj = ticket_update.scalar_one_or_none()
                    
                    if not ticket_obj:
                        return
                    
                    # Use enhanced auto-assignment with team-based routing
                    assignment_result = await routing_service.auto_assign_ticket_if_confident(
                        ticket_id=ticket_id,
                        confidence_threshold=0.80  # Lowered for demo purposes
                    )
                    
                    # Get routing recommendation for detailed info
                    routing_recommendation = await routing_service.route_ticket(ticket_id)
                    
                    # Initialize comments list if needed
                    if not ticket_obj.comments:
                        ticket_obj.comments = []
                    
                    # Create separate comments for each piece of information
                    recommended_agent = routing_recommendation.recommended_agent
                    
                    # Comment 1: Category
                    category_comment = {
                        "user": "AI Assistant",
                        "text": f"Category: {ticket_obj.category}",
                        "time": datetime.now(timezone.utc).isoformat()
                    }
                    ticket_obj.comments.append(category_comment)
                    
                    # Comment 2: Recommended Agent
                    if recommended_agent:
                        agent_comment = {
                            "user": "AI Assistant",
                            "text": f"Recommended Agent: {recommended_agent.agent_name}",
                            "time": datetime.now(timezone.utc).isoformat()
                        }
                        ticket_obj.comments.append(agent_comment)
                    
                    # Comment 3: Recommended Team
                    if routing_recommendation.team_recommendation:
                        team_comment = {
                            "user": "AI Assistant",
                            "text": f"Recommended Team: {routing_recommendation.team_recommendation}",
                            "time": datetime.now(timezone.utc).isoformat()
                        }
                        ticket_obj.comments.append(team_comment)
                    
                    # Comment 4: Availability
                    if recommended_agent:
                        availability_comment = {
                            "user": "AI Assistant",
                            "text": f"Availability: {recommended_agent.availability}",
                            "time": datetime.now(timezone.utc).isoformat()
                        }
                        ticket_obj.comments.append(availability_comment)
                    
                    # Comment 5: Assignment status (if auto-assigned)
                    if assignment_result.get("auto_assigned"):
                        assigned_agent = assignment_result['assigned_agent']
                        assignment_comment = {
                            "user": "System",
                            "text": f"Ticket assigned to {assigned_agent['name']}",
                            "time": datetime.now(timezone.utc).isoformat()
                        }
                        ticket_obj.comments.append(assignment_comment)
            
            await db.commit()
            
        except Exception as e:
            print(f"Error in AI enhancement: {e}")
            await db.rollback()

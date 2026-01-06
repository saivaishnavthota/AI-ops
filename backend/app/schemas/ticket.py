from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class TicketCommentBase(BaseModel):
    """Ticket comment schema."""

    user: str
    text: str
    time: str


class TicketBase(BaseModel):
    """Base ticket schema."""

    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assignee_name: Optional[str] = None


class TicketCreate(TicketBase):
    """Ticket creation schema."""

    subject: str = Field(..., min_length=1, max_length=500)
    description: str
    priority: str
    category: str


class TicketUpdate(BaseModel):
    """Ticket update schema."""

    status: Optional[str] = None
    assignee_id: Optional[UUID] = None
    assignee_name: Optional[str] = None
    comments: Optional[List[Dict[str, Any]]] = None


class TicketResponse(BaseSchema):
    """Ticket response schema."""

    id: UUID
    organization_id: UUID
    subject: str
    description: str
    status: str
    priority: str
    category: str
    requester_id: Optional[UUID]
    requester_name: str
    assignee_id: Optional[UUID]
    assignee_name: Optional[str]
    comments: List[Dict[str, Any]]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class TicketListResponse(PaginatedResponse[TicketResponse]):
    """Paginated ticket list response."""

    pass


class KnowledgeBaseArticleBase(BaseModel):
    """Base knowledge base article schema."""

    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class KnowledgeBaseArticleCreate(KnowledgeBaseArticleBase):
    """Knowledge base article creation schema."""

    title: str = Field(..., min_length=1, max_length=500)
    excerpt: str
    content: str
    category: str
    tags: List[str] = []


class KnowledgeBaseArticleUpdate(KnowledgeBaseArticleBase):
    """Knowledge base article update schema."""

    is_published: Optional[bool] = None


class KnowledgeBaseArticleResponse(BaseSchema):
    """Knowledge base article response schema."""

    id: UUID
    organization_id: UUID
    title: str
    excerpt: str
    content: str
    category: str
    tags: List[str]
    views: int
    helpful_count: int
    author_id: Optional[UUID]
    is_published: bool
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseArticleListResponse(PaginatedResponse[KnowledgeBaseArticleResponse]):
    """Paginated knowledge base article list response."""

    pass

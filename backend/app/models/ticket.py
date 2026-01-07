from sqlalchemy import Column, String, ForeignKey, Text, JSON, DateTime, Integer, Boolean
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class TicketStatus(str, enum.Enum):
    """Ticket status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    """Ticket priority."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Ticket(BaseModel):
    """Service desk tickets."""

    __tablename__ = "tickets"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Ticket details
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default=TicketStatus.OPEN.value, index=True)
    priority = Column(String(20), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    
    # People
    requester_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    requester_name = Column(String(255), nullable=False)
    assignee_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    assignee_name = Column(String(255), nullable=True)
    
    # Comments stored as JSON array
    comments = Column(JSON, default=list)
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="tickets")

    def __repr__(self) -> str:
        try:
            return f"<Ticket {self.id} - {self.subject}>"
        except:
            return f"<Ticket id={self.id}>"


class KnowledgeBaseArticle(BaseModel):
    """Knowledge base articles."""

    __tablename__ = "kb_articles"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Article content
    title = Column(String(500), nullable=False)
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    views = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    # Author
    author_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Source ticket (if created from ticket resolution)
    source_ticket_id = Column(
        GUID(),
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Publishing
    is_published = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="kb_articles")

    def __repr__(self) -> str:
        try:
            return f"<KBArticle {self.title}>"
        except:
            return f"<KBArticle id={self.id}>"

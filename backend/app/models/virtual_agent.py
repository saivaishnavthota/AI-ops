"""
Virtual Agent models for AI-first Service Desk.

Handles chat conversations, agent responses, and learning from interactions.
"""

from sqlalchemy import Column, String, ForeignKey, Text, JSON, DateTime, Boolean, Integer, Float
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class ConversationStatus(str, enum.Enum):
    """Conversation status."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"


class MessageType(str, enum.Enum):
    """Message type."""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ResolutionType(str, enum.Enum):
    """How the conversation was resolved."""
    SELF_SERVICE = "self_service"
    VIRTUAL_AGENT = "virtual_agent"
    HUMAN_ESCALATION = "human_escalation"
    KB_ARTICLE = "kb_article"
    AUTOMATED = "automated"


class Conversation(BaseModel):
    """Virtual agent conversation."""

    __tablename__ = "conversations"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User information
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=True)

    # Conversation details
    subject = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    priority = Column(String(20), nullable=True, index=True)
    status = Column(String(20), default=ConversationStatus.ACTIVE.value, index=True)

    # AI Analysis
    intent = Column(String(100), nullable=True)  # password_reset, access_request, etc.
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    confidence = Column(Float, nullable=True)
    language = Column(String(10), default="en")

    # Resolution tracking
    resolution_type = Column(String(30), nullable=True)
    resolved_by_agent_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_time_seconds = Column(Integer, nullable=True)

    # Related entities
    ticket_id = Column(
        GUID(),
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
    )
    kb_articles_suggested = Column(JSON, default=list)  # List of article IDs
    kb_articles_helpful = Column(JSON, default=list)  # Articles marked as helpful

    # Satisfaction
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    satisfaction_feedback = Column(Text, nullable=True)

    # Metadata
    extra_metadata = Column(JSON, default=dict)  # Additional context, tags, etc.

    # Relationships
    organization = relationship("Organization")
    user = relationship("User", foreign_keys=[user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_agent_id])
    ticket = relationship("Ticket")
    messages = relationship("ConversationMessage", back_populates="conversation", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Conversation {self.id} - {self.subject}>"


class ConversationMessage(BaseModel):
    """Messages within a conversation."""

    __tablename__ = "conversation_messages"

    conversation_id = Column(
        GUID(),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message details
    message_type = Column(String(20), nullable=False)  # user, agent, system
    content = Column(Text, nullable=False)
    
    # Sender information
    sender_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    sender_name = Column(String(255), nullable=True)

    # AI processing
    processed_by_ai = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)
    ai_suggestions = Column(JSON, default=list)  # AI-generated response suggestions
    
    # Response metadata
    response_time_ms = Column(Integer, nullable=True)
    kb_articles_referenced = Column(JSON, default=list)
    actions_taken = Column(JSON, default=list)  # password_reset, account_unlock, etc.

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")

    def __repr__(self) -> str:
        return f"<Message {self.id} - {self.message_type}>"


class VirtualAgentKnowledge(BaseModel):
    """Virtual agent knowledge base for organization-specific training."""

    __tablename__ = "virtual_agent_knowledge"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Knowledge entry
    category = Column(String(100), nullable=False, index=True)
    intent = Column(String(100), nullable=False, index=True)
    keywords = Column(JSON, default=list)
    
    # Response templates
    response_template = Column(Text, nullable=False)
    follow_up_questions = Column(JSON, default=list)
    required_actions = Column(JSON, default=list)
    
    # Automation capabilities
    can_auto_resolve = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    escalation_triggers = Column(JSON, default=list)
    
    # Learning metrics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")

    def __repr__(self) -> str:
        return f"<VirtualAgentKnowledge {self.intent} - {self.category}>"


class AgentPerformance(BaseModel):
    """Track agent performance metrics for AI assistance."""

    __tablename__ = "agent_performance"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Time period (daily metrics)
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Volume metrics
    tickets_handled = Column(Integer, default=0)
    conversations_handled = Column(Integer, default=0)
    escalations_received = Column(Integer, default=0)

    # Quality metrics
    avg_resolution_time_minutes = Column(Float, default=0.0)
    first_contact_resolution_rate = Column(Float, default=0.0)
    customer_satisfaction_avg = Column(Float, default=0.0)
    
    # AI assistance metrics
    ai_suggestions_used = Column(Integer, default=0)
    ai_suggestions_available = Column(Integer, default=0)
    kb_articles_referenced = Column(Integer, default=0)
    
    # Skill areas (JSON with categories and proficiency scores)
    skill_scores = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization")
    agent = relationship("User")

    def __repr__(self) -> str:
        return f"<AgentPerformance {self.agent_id} - {self.date}>"
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from app.models.base import BaseModel


class ResourceStatus(str, enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PENDING = "pending"
    ERROR = "error"


class RecommendationImpact(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    APPLIED = "applied"
    DISMISSED = "dismissed"


class CloudResource(BaseModel):
    __tablename__ = "cloud_resources"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)  # EC2, RDS, S3, etc.
    provider = Column(String(50), nullable=False)  # AWS, Azure, GCP
    region = Column(String(100), nullable=False)
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.RUNNING, nullable=False)
    
    # Resource specs
    instance_type = Column(String(100))
    cpu_usage = Column(Float, default=0)  # Percentage
    memory_usage = Column(Float, default=0)  # Percentage
    
    # Network
    private_ip = Column(String(50))
    public_ip = Column(String(50))
    
    # Cost
    monthly_cost = Column(Float, default=0)
    
    # Metadata
    launch_time = Column(DateTime)
    resource_metadata = Column(JSON)  # Additional provider-specific data
    
    # Relationships
    cost_items = relationship("CloudCostItem", back_populates="resource", cascade="all, delete-orphan")


class CloudCostItem(BaseModel):
    __tablename__ = "cloud_cost_items"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("cloud_resources.id", ondelete="CASCADE"), nullable=True)
    
    service = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Compute, Storage, Database, Network, etc.
    
    # Costs
    current_month = Column(Float, default=0)
    last_month = Column(Float, default=0)
    budget = Column(Float, default=0)
    
    # Period
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Details
    details = Column(JSON)  # Resource breakdown
    
    # Relationships
    resource = relationship("CloudResource", back_populates="cost_items")


class CloudOptimizationRecommendation(BaseModel):
    __tablename__ = "cloud_optimization_recommendations"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("cloud_resources.id", ondelete="SET NULL"), nullable=True)
    
    recommendation_type = Column(String(100), nullable=False)  # Right-sizing, Reserved Instance, etc.
    resource_name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    
    impact = Column(SQLEnum(RecommendationImpact), nullable=False)
    monthly_savings = Column(Float, default=0)
    effort = Column(String(50), nullable=False)  # Low, Medium, High
    
    status = Column(SQLEnum(RecommendationStatus), default=RecommendationStatus.PENDING, nullable=False)
    ai_confidence = Column(Float, default=0)  # 0-1
    
    # Implementation
    implementation_steps = Column(JSON)  # List of steps
    
    # Tracking
    applied_at = Column(DateTime)
    dismissed_at = Column(DateTime)
    
    # Relationships
    resource = relationship("CloudResource")

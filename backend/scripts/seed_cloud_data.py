"""
Seed cloud resources, costs, and optimization recommendations data.
Run this script to populate the database with demo cloud data.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import uuid

from app.config.settings import settings
from app.models.cloud import (
    CloudResource,
    CloudCostItem,
    CloudOptimizationRecommendation,
    ResourceStatus,
    RecommendationImpact,
    RecommendationStatus
)
from app.models.organization import Organization


async def seed_cloud_data():
    """Seed cloud data."""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get first organization
        from sqlalchemy import select
        result = await session.execute(select(Organization).limit(1))
        org = result.scalar_one_or_none()
        
        if not org:
            print("No organization found. Please run seed_demo_data.py first.")
            return
        
        print(f"Seeding cloud data for organization: {org.name}")
        
        # Create cloud resources
        resources_data = [
            {
                "name": "prod-api-server-1",
                "resource_type": "EC2",
                "provider": "AWS",
                "region": "us-east-1",
                "status": ResourceStatus.RUNNING,
                "instance_type": "t3.large",
                "cpu_usage": 45.0,
                "memory_usage": 62.0,
                "monthly_cost": 156.50,
                "private_ip": "10.0.1.15",
                "public_ip": "54.123.45.67",
                "launch_time": datetime.utcnow() - timedelta(days=45)
            },
            {
                "name": "prod-api-server-2",
                "resource_type": "EC2",
                "provider": "AWS",
                "region": "us-east-1",
                "status": ResourceStatus.RUNNING,
                "instance_type": "t3.large",
                "cpu_usage": 38.0,
                "memory_usage": 55.0,
                "monthly_cost": 156.50,
                "private_ip": "10.0.1.16",
                "public_ip": "54.123.45.68",
                "launch_time": datetime.utcnow() - timedelta(days=45)
            },
            {
                "name": "prod-db-primary",
                "resource_type": "RDS",
                "provider": "AWS",
                "region": "us-east-1",
                "status": ResourceStatus.RUNNING,
                "instance_type": "db.r5.xlarge",
                "cpu_usage": 72.0,
                "memory_usage": 85.0,
                "monthly_cost": 450.00,
                "private_ip": "10.0.2.10",
                "launch_time": datetime.utcnow() - timedelta(days=90)
            },
            {
                "name": "prod-db-replica",
                "resource_type": "RDS",
                "provider": "AWS",
                "region": "us-west-2",
                "status": ResourceStatus.RUNNING,
                "instance_type": "db.r5.large",
                "cpu_usage": 25.0,
                "memory_usage": 40.0,
                "monthly_cost": 350.00,
                "private_ip": "10.1.2.10",
                "launch_time": datetime.utcnow() - timedelta(days=90)
            },
            {
                "name": "prod-redis-cluster",
                "resource_type": "ElastiCache",
                "provider": "AWS",
                "region": "us-east-1",
                "status": ResourceStatus.RUNNING,
                "instance_type": "cache.r5.large",
                "cpu_usage": 15.0,
                "memory_usage": 45.0,
                "monthly_cost": 89.00,
                "private_ip": "10.0.3.5",
                "launch_time": datetime.utcnow() - timedelta(days=120)
            },
            {
                "name": "staging-api-server",
                "resource_type": "EC2",
                "provider": "AWS",
                "region": "us-east-1",
                "status": ResourceStatus.STOPPED,
                "instance_type": "t3.medium",
                "cpu_usage": 0,
                "memory_usage": 0,
                "monthly_cost": 0,
                "private_ip": "10.0.4.10",
                "launch_time": datetime.utcnow() - timedelta(days=30)
            },
            {
                "name": "dev-kubernetes-cluster",
                "resource_type": "EKS",
                "provider": "AWS",
                "region": "us-west-2",
                "status": ResourceStatus.RUNNING,
                "instance_type": "3 nodes",
                "cpu_usage": 55.0,
                "memory_usage": 70.0,
                "monthly_cost": 245.00,
                "private_ip": "10.1.0.0/16",
                "launch_time": datetime.utcnow() - timedelta(days=150)
            },
            {
                "name": "cdn-distribution",
                "resource_type": "CloudFront",
                "provider": "AWS",
                "region": "global",
                "status": ResourceStatus.RUNNING,
                "cpu_usage": 0,
                "memory_usage": 0,
                "monthly_cost": 125.00,
                "launch_time": datetime.utcnow() - timedelta(days=200)
            },
        ]
        
        resources = []
        for data in resources_data:
            resource = CloudResource(
                organization_id=org.id,
                **data
            )
            session.add(resource)
            resources.append(resource)
        
        await session.flush()
        print(f"Created {len(resources)} cloud resources")
        
        # Create cost items
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        
        costs_data = [
            {
                "service": "EC2 Instances",
                "category": "Compute",
                "current_month": 2450.00,
                "last_month": 2380.00,
                "budget": 3000,
                "details": [
                    {"resource": "prod-api-server-1", "cost": 850, "usage": "720 hours"},
                    {"resource": "prod-api-server-2", "cost": 850, "usage": "720 hours"},
                    {"resource": "staging-api-server", "cost": 350, "usage": "400 hours"},
                    {"resource": "dev-server", "cost": 400, "usage": "500 hours"},
                ]
            },
            {
                "service": "RDS Databases",
                "category": "Database",
                "current_month": 1850.00,
                "last_month": 1750.00,
                "budget": 2000,
                "details": [
                    {"resource": "prod-db-primary", "cost": 1200, "usage": "720 hours"},
                    {"resource": "prod-db-replica", "cost": 650, "usage": "720 hours"},
                ]
            },
            {
                "service": "S3 Storage",
                "category": "Storage",
                "current_month": 450.00,
                "last_month": 420.00,
                "budget": 500,
                "details": [
                    {"resource": "prod-assets", "cost": 200, "usage": "500 GB"},
                    {"resource": "prod-backups", "cost": 150, "usage": "300 GB"},
                    {"resource": "prod-logs", "cost": 100, "usage": "200 GB"},
                ]
            },
            {
                "service": "CloudFront CDN",
                "category": "Network",
                "current_month": 320.00,
                "last_month": 380.00,
                "budget": 400,
                "details": [
                    {"resource": "cdn-distribution", "cost": 320, "usage": "2.5 TB transfer"},
                ]
            },
            {"service": "EKS Cluster", "category": "Compute", "current_month": 890.00, "last_month": 850.00, "budget": 1000},
            {"service": "ElastiCache", "category": "Database", "current_month": 280.00, "last_month": 280.00, "budget": 300},
            {"service": "Lambda Functions", "category": "Compute", "current_month": 125.00, "last_month": 110.00, "budget": 200},
            {"service": "CloudWatch", "category": "Monitoring", "current_month": 85.00, "last_month": 80.00, "budget": 100},
        ]
        
        for data in costs_data:
            cost = CloudCostItem(
                organization_id=org.id,
                month=current_month,
                year=current_year,
                **data
            )
            session.add(cost)
        
        print(f"Created {len(costs_data)} cost items")
        
        # Create optimization recommendations
        recommendations_data = [
            {
                "recommendation_type": "Right-sizing",
                "resource_name": "prod-api-server-2",
                "description": "Instance is consistently underutilized (avg CPU 15%). Consider downsizing from m5.xlarge to m5.large.",
                "impact": RecommendationImpact.HIGH,
                "monthly_savings": 52.50,
                "effort": "Low",
                "status": RecommendationStatus.PENDING,
                "ai_confidence": 0.92,
                "implementation_steps": [
                    "Create a snapshot of the current instance",
                    "Launch a new m5.large instance with the same configuration",
                    "Migrate traffic to the new instance",
                    "Verify application performance",
                    "Terminate the old m5.xlarge instance",
                ],
            },
            {
                "recommendation_type": "Reserved Instance",
                "resource_name": "prod-db-primary",
                "description": "This instance has been running continuously for 6 months. Reserved Instance would save 40%.",
                "impact": RecommendationImpact.HIGH,
                "monthly_savings": 180.00,
                "effort": "Low",
                "status": RecommendationStatus.PENDING,
                "ai_confidence": 0.95,
                "implementation_steps": [
                    "Review current RDS instance usage patterns",
                    "Calculate 1-year vs 3-year reserved instance pricing",
                    "Purchase reserved instance through AWS Console",
                    "Savings will be applied automatically",
                ],
            },
            {
                "recommendation_type": "Unused Resource",
                "resource_name": "staging-api-server",
                "description": "Instance has been stopped for 30+ days. Consider terminating or archiving.",
                "impact": RecommendationImpact.LOW,
                "monthly_savings": 15.00,
                "effort": "Low",
                "status": RecommendationStatus.PENDING,
                "ai_confidence": 0.88,
                "implementation_steps": [
                    "Confirm instance is no longer needed",
                    "Create AMI backup if preservation is required",
                    "Terminate the stopped instance",
                    "Delete associated EBS volumes",
                ],
            },
            {
                "recommendation_type": "Storage Optimization",
                "resource_name": "prod-logs-bucket",
                "description": "Move infrequently accessed logs (>90 days) to S3 Glacier for 80% cost reduction.",
                "impact": RecommendationImpact.MEDIUM,
                "monthly_savings": 85.00,
                "effort": "Medium",
                "status": RecommendationStatus.APPLIED,
                "ai_confidence": 0.91,
            },
            {
                "recommendation_type": "Network Optimization",
                "resource_name": "NAT Gateway",
                "description": "High data transfer costs detected. Consider VPC endpoints for S3 and DynamoDB.",
                "impact": RecommendationImpact.MEDIUM,
                "monthly_savings": 120.00,
                "effort": "Medium",
                "status": RecommendationStatus.PENDING,
                "ai_confidence": 0.85,
                "implementation_steps": [
                    "Create VPC endpoint for S3",
                    "Create VPC endpoint for DynamoDB",
                    "Update route tables to use VPC endpoints",
                    "Monitor NAT Gateway data transfer reduction",
                ],
            },
        ]
        
        for data in recommendations_data:
            recommendation = CloudOptimizationRecommendation(
                organization_id=org.id,
                **data
            )
            session.add(recommendation)
        
        print(f"Created {len(recommendations_data)} optimization recommendations")
        
        await session.commit()
        print("\n✅ Cloud data seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_cloud_data())

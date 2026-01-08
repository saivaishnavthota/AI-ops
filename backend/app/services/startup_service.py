"""
Startup Service
Handles application startup tasks including auto ticket generation
"""

import logging
import asyncio
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.services.auto_ticket_generator import auto_ticket_generator

logger = logging.getLogger(__name__)


class StartupService:
    """Service to handle application startup tasks."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize_application(self):
        """Initialize the application with startup tasks."""
        if self.initialized:
            logger.info("Application already initialized")
            return
        
        logger.info("🚀 Initializing AI-Ops Platform...")
        
        try:
            # Wait a bit for database to be ready
            await asyncio.sleep(2)
            
            # Start auto ticket generation
            await self._start_auto_ticket_generation()
            
            self.initialized = True
            logger.info("✅ Application initialization completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Application initialization failed: {e}")
            raise
    
    async def _start_auto_ticket_generation(self):
        """Start automatic ticket generation."""
        try:
            async with AsyncSessionLocal() as db:
                # Check if we have any organizations with admin users
                admin_result = await db.execute(
                    select(User.organization_id).where(
                        User.is_active == True,
                        User.role.in_([UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value])
                    ).limit(1)
                )
                
                org_row = admin_result.first()
                if not org_row:
                    logger.warning("No admin users found - skipping auto ticket generation")
                    return
                
                organization_id = org_row[0]
                
                # Start auto ticket generation with 2-minute intervals
                await auto_ticket_generator.start_auto_generation(
                    interval_minutes=2,
                    organization_id=organization_id
                )
                
                logger.info("🎫 Auto ticket generation started successfully")
                
        except Exception as e:
            logger.error(f"Failed to start auto ticket generation: {e}")
            # Don't raise - let the app continue without auto generation
    
    async def shutdown_application(self):
        """Shutdown the application gracefully."""
        logger.info("🛑 Shutting down AI-Ops Platform...")
        
        try:
            # Stop auto ticket generation
            await auto_ticket_generator.stop_auto_generation()
            
            logger.info("✅ Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")


# Global instance
startup_service = StartupService()
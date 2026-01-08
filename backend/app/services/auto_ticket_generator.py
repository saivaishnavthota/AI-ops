"""
Auto Ticket Generator Service
Generates tickets automatically using the logic from the GitHub ticketing system
"""

import logging
import asyncio
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta, timedelta
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import AsyncSessionLocal
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import User, UserRole
from app.models.notification import NotificationType, NotificationPriority
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class AutoTicketGenerator:
    """Service to automatically generate tickets using predefined templates."""
    
    def __init__(self):
        self.is_running = False
        self.ticket_count = 0
        self.start_time: Optional[datetime] = None
        self.task: Optional[asyncio.Task] = None
        
        # Ticket templates from the GitHub system
        self.templates = {
            "subjects": [
                'Email server not responding',
                'Unable to access shared drive',
                'Printer not working in office',
                'VPN connection issues',
                'Application crashes on startup',
                'Database connection timeout',
                'Website loading slowly',
                'Password reset not working',
                'File server disk space full',
                'Network connectivity issues',
                'Software license expired',
                'Backup job failed',
                'Security certificate expired',
                'User account locked out',
                'Phone system down',
                'Video conferencing not working',
                'Mobile app sync issues',
                'Report generation failing',
                'API endpoint returning errors',
                'System performance degradation',
                'Login page not loading',
                'File upload functionality broken',
                'Email notifications not sending',
                'Calendar integration issues',
                'Remote desktop connection failed',
                'Cloud storage synchronization failed',
                'Multi-factor authentication not working',
                'SSL certificate renewal required',
                'Load balancer health check failing',
                'Microservice communication timeout',
                'Container orchestration issues',
                'CI/CD pipeline deployment failure',
                'Monitoring alerts not triggering',
                'Log aggregation service down',
                'Message queue processing delays'
            ],
            "descriptions": [
                'Users are experiencing intermittent connectivity issues when trying to access the service.',
                'The system appears to be running slowly and users are reporting timeout errors.',
                'Multiple users have reported that they cannot complete their daily tasks due to this issue.',
                'The service has been unavailable for the past 30 minutes affecting productivity.',
                'Error messages are appearing when users try to perform routine operations.',
                'The application is crashing unexpectedly during peak usage hours.',
                'Users are unable to save their work and are losing data.',
                'The system is returning HTTP 500 errors when processing requests.',
                'Performance has degraded significantly since the last update.',
                'Users are experiencing authentication failures when logging in.',
                'The service is not responding to requests and appears to be down.',
                'Data synchronization between systems has stopped working.',
                'Users report that the interface is not loading properly.',
                'Critical business processes are being impacted by this outage.',
                'The system is generating excessive error logs and alerts.',
                'Users cannot access important files needed for their work.',
                'The service is experiencing high latency and slow response times.',
                'Automated processes are failing to complete successfully.',
                'Users are seeing blank pages instead of the expected content.',
                'The system is not processing transactions correctly.',
                'Memory usage has increased significantly causing system instability.',
                'Database queries are timing out during peak hours.',
                'Third-party API integrations are returning error responses.',
                'Scheduled maintenance tasks are not executing as expected.',
                'User sessions are being terminated unexpectedly.',
                'File permissions have been corrupted affecting access.',
                'Network latency has increased causing application slowdowns.',
                'Backup verification process is reporting data integrity issues.',
                'Security scanning has detected potential vulnerabilities.',
                'Resource utilization metrics are showing abnormal patterns.'
            ],
            "categories": [
                'Access Issue',
                'Service Request', 
                'Performance',
                'Bug Report',
                'Network',
                'Security',
                'Hardware',
                'Software',
                'Database',
                'Infrastructure',
                'Cloud Services',
                'Integration',
                'Monitoring',
                'Backup & Recovery',
                'User Management'
            ],
            "requester_names": [
                'John Smith',
                'Sarah Johnson', 
                'Michael Brown',
                'Emily Davis',
                'David Wilson',
                'Lisa Anderson',
                'Robert Taylor',
                'Jennifer Martinez',
                'Christopher Lee',
                'Amanda White',
                'Matthew Garcia',
                'Jessica Rodriguez',
                'Daniel Thompson',
                'Ashley Martinez',
                'James Anderson',
                'Michelle Thomas',
                'Kevin Jackson',
                'Stephanie White',
                'Brian Harris',
                'Nicole Clark',
                'Ryan Lewis',
                'Samantha Walker',
                'Justin Hall',
                'Rachel Allen',
                'Brandon Young',
                'Maria Gonzalez',
                'Tyler Moore',
                'Kimberly Taylor',
                'Andrew Miller',
                'Laura Wilson'
            ]
        }
        
        # Priority distribution: Low: 40%, Medium: 35%, High: 20%, Urgent: 5%
        self.priority_weights = [
            ('low', 0.40),
            ('normal', 0.35), 
            ('high', 0.20),
            ('urgent', 0.05)
        ]
    
    async def start_auto_generation(self, interval_minutes: int = 3, organization_id: Optional[UUID] = None):
        """Start automatic ticket generation."""
        if self.is_running:
            logger.warning("Auto ticket generation is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now(timezone.utc)
        self.ticket_count = 0
        
        logger.info(f"🎫 Starting automatic ticket generation every {interval_minutes} minutes")
        
        # Generate first ticket immediately
        await self._generate_ticket(organization_id)
        
        # Start background task for periodic generation
        self.task = asyncio.create_task(
            self._periodic_generation(interval_minutes, organization_id)
        )
    
    async def stop_auto_generation(self):
        """Stop automatic ticket generation."""
        if not self.is_running:
            logger.warning("Auto ticket generation is not running")
            return
        
        self.is_running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        
        end_time = datetime.now(timezone.utc)
        duration = self.start_time and (end_time - self.start_time).total_seconds() / 60
        
        logger.info(f"🛑 Stopped automatic ticket generation. Generated {self.ticket_count} tickets over {duration:.1f} minutes")
    
    async def generate_single_ticket(self, organization_id: Optional[UUID] = None) -> Optional[Ticket]:
        """Generate a single ticket manually."""
        return await self._generate_ticket(organization_id)
    
    async def _periodic_generation(self, interval_minutes: int, organization_id: Optional[UUID]):
        """Background task for periodic ticket generation."""
        try:
            while self.is_running:
                await asyncio.sleep(interval_minutes * 60)  # Convert to seconds
                if self.is_running:  # Check again after sleep
                    await self._generate_ticket(organization_id)
        except asyncio.CancelledError:
            logger.info("Periodic ticket generation cancelled")
        except Exception as e:
            logger.error(f"Error in periodic ticket generation: {e}")
            self.is_running = False
    
    async def _generate_ticket(self, organization_id: Optional[UUID] = None) -> Optional[Ticket]:
        """Generate a single ticket."""
        async with AsyncSessionLocal() as db:
            try:
                # Get a random organization if not specified
                if not organization_id:
                    org_result = await db.execute(
                        select(User.organization_id).where(
                            User.is_active == True,
                            User.role.in_([UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value])
                        ).limit(1)
                    )
                    org_row = org_result.first()
                    if not org_row:
                        logger.warning("No active organizations found for ticket generation")
                        return None
                    organization_id = org_row[0]
                
                # Get a random user from the organization for admin notifications only
                user_result = await db.execute(
                    select(User).where(
                        User.organization_id == organization_id,
                        User.is_active == True
                    ).limit(1)  # Just need one user for organization reference
                )
                users = user_result.scalars().all()
                
                if not users:
                    logger.warning(f"No active users found in organization {organization_id}")
                    return None
                
                # Use the first user just for organization reference, but use mock requester
                reference_user = users[0]
                
                # Generate ticket data
                ticket_data = self._generate_ticket_data()
                
                # Select a random mock requester name
                mock_requester_name = random.choice(self.templates['requester_names'])
                
                # Create the ticket with enhanced AI comments
                ai_comments = self._generate_ai_comments(ticket_data, reference_user)
                
                ticket = Ticket(
                    organization_id=organization_id,
                    requester_id=reference_user.id,  # Use reference user ID for database constraints
                    requester_name=mock_requester_name,  # Use mock name for display
                    subject=ticket_data['subject'],
                    description=ticket_data['description'],
                    status='open',
                    priority=ticket_data['priority'],
                    category=ticket_data['category'],
                    comments=ai_comments
                )
                
                db.add(ticket)
                await db.commit()
                await db.refresh(ticket)
                
                self.ticket_count += 1
                
                logger.info(f"✅ Auto-generated ticket #{self.ticket_count}: {ticket.subject}")
                logger.info(f"   Priority: {ticket.priority} | Category: {ticket.category} | Requester: {mock_requester_name}")
                
                # Send notification to admins about new ticket
                try:
                    notification_service = NotificationService(db)
                    
                    # Get admin users to notify
                    admin_result = await db.execute(
                        select(User).where(
                            User.organization_id == organization_id,
                            User.is_active == True,
                            User.role.in_([UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value])
                        )
                    )
                    admins = admin_result.scalars().all()
                    
                    for admin in admins:
                        await notification_service.create_notification(
                            user_id=admin.id,
                            organization_id=organization_id,
                            title="New Auto-Generated Ticket",
                            message=f"Ticket '{ticket.subject}' has been automatically created",
                            type=NotificationType.INFO,
                            priority=NotificationPriority.MEDIUM,
                            action_url=f"/tickets/{ticket.id}",
                            action_label="View Ticket",
                            related_entity_type="ticket",
                            related_entity_id=str(ticket.id)
                        )
                
                except Exception as e:
                    logger.warning(f"Failed to send notifications for auto-generated ticket: {e}")
                
                return ticket
                
            except Exception as e:
                logger.error(f"❌ Failed to auto-generate ticket: {e}")
                await db.rollback()
                return None
    
    def _generate_ticket_data(self) -> Dict[str, Any]:
        """Generate random ticket data using templates."""
        subject = random.choice(self.templates['subjects'])
        description = random.choice(self.templates['descriptions'])
        category = random.choice(self.templates['categories'])
        
        # Generate priority based on weighted distribution
        rand = random.random()
        cumulative = 0
        priority = 'normal'  # default
        
        for prio, weight in self.priority_weights:
            cumulative += weight
            if rand <= cumulative:
                priority = prio
                break
        
        return {
            'subject': subject,
            'description': description,
            'category': category,
            'priority': priority
        }
    
    def _generate_ai_comments(self, ticket_data: Dict[str, Any], requester: User) -> List[Dict[str, Any]]:
        """Generate AI Assistant comments for the ticket as separate entries."""
        category = ticket_data['category']
        priority = ticket_data['priority']
        subject = ticket_data['subject']
        
        # AI analysis based on category and priority
        recommended_agent = self._get_recommended_agent(category, priority)
        
        # Generate timestamp for AI comments
        base_timestamp = datetime.now(timezone.utc)
        
        # Create separate AI comments for each section
        ai_comments = []
        
        # 1. Category Analysis Comment
        ai_comments.append({
            "id": f"ai_category_{int(base_timestamp.timestamp())}",
            "author": "AI Assistant",
            "author_role": "system",
            "content": f"Category: {category}",
            "timestamp": base_timestamp.isoformat(),
            "is_internal": False,
            "attachments": []
        })
        
        # 2. Recommended Agent Comment (1 second later)
        agent_timestamp = base_timestamp + timedelta(seconds=1)
        recommended_agent_name = self._extract_agent_name(recommended_agent)
        ai_comments.append({
            "id": f"ai_agent_{int(agent_timestamp.timestamp())}",
            "author": "AI Assistant", 
            "author_role": "system",
            "content": f"Recommended Agent: {recommended_agent_name}",
            "timestamp": agent_timestamp.isoformat(),
            "is_internal": False,
            "attachments": []
        })
        
        return ai_comments
    
    def _extract_agent_name(self, recommended_agent: str) -> str:
        """Extract clean agent name from recommendation."""
        # Remove urgency notes in parentheses
        if " (" in recommended_agent and recommended_agent.endswith(")"):
            parts = recommended_agent.split(" (")
            if len(parts) >= 2:
                # Keep the name and role, remove urgency
                name_and_role = parts[0]
                if " (" in name_and_role:
                    return name_and_role
                else:
                    # If no role in parentheses, just return the name
                    return name_and_role
        return recommended_agent
    
    def _get_category_analysis(self, category: str, priority: str) -> str:
        """Generate category-specific analysis."""
        analyses = {
            'Access Issue': f"Access-related incident detected. Typical resolution involves credential verification and permission auditing. Expected resolution time: {'15-30 minutes' if priority in ['low', 'normal'] else '5-15 minutes'}.",
            'Service Request': f"Standard service request identified. Requires workflow approval and resource allocation. Processing time varies based on request complexity.",
            'Performance': f"Performance degradation detected. Requires system monitoring analysis and resource optimization. Critical for user productivity.",
            'Bug Report': f"Software defect reported. Needs developer investigation and potential code fix. Impact assessment required.",
            'Network': f"Network connectivity issue identified. Requires infrastructure team investigation and potential hardware diagnostics.",
            'Security': f"Security-related incident. Immediate attention required. May need compliance review and audit trail documentation.",
            'Hardware': f"Hardware malfunction reported. Physical inspection and potential replacement may be required. Vendor support might be needed.",
            'Software': f"Software-related issue detected. May require application restart, configuration changes, or software updates.",
            'Database': f"Database connectivity or performance issue. DBA investigation required. Data integrity checks recommended.",
            'Infrastructure': f"Infrastructure component failure. System architecture review needed. High impact on multiple services possible.",
            'Cloud Services': f"Cloud platform issue detected. Vendor status check required. May involve service provider escalation.",
            'Integration': f"System integration failure identified. API connectivity and data flow analysis needed.",
            'Monitoring': f"Monitoring system alert or failure. Observability stack investigation required. May indicate broader system issues.",
            'Backup & Recovery': f"Backup or recovery process failure. Data protection protocols activated. Business continuity assessment needed.",
            'User Management': f"User account or permission issue. Identity management system review required. Security implications possible."
        }
        
        return analyses.get(category, f"General {category.lower()} issue requiring standard troubleshooting procedures.")
    
    def _get_recommended_agent(self, category: str, priority: str) -> str:
        """Get recommended agent based on category and priority."""
        # Agent recommendations based on category expertise
        agent_mapping = {
            'Access Issue': ['Sarah Chen (Identity Specialist)', 'Mike Rodriguez (Access Control)', 'Lisa Park (Security Admin)'],
            'Service Request': ['Jennifer Walsh (Service Coordinator)', 'David Kim (Request Handler)', 'Amanda Foster (Workflow Manager)'],
            'Performance': ['Alex Thompson (Performance Engineer)', 'Rachel Green (System Optimizer)', 'Tom Wilson (Infrastructure)'],
            'Bug Report': ['Chris Martinez (Senior Developer)', 'Emily Johnson (QA Lead)', 'Kevin Lee (Software Engineer)'],
            'Network': ['Robert Chang (Network Engineer)', 'Maria Santos (Infrastructure)', 'James Liu (Connectivity Specialist)'],
            'Security': ['Dr. Patricia Moore (Security Lead)', 'Steven Taylor (Cybersecurity)', 'Nicole Brown (Compliance Officer)'],
            'Hardware': ['Michael O\'Connor (Hardware Tech)', 'Jessica Wang (Field Engineer)', 'Daniel Garcia (Equipment Specialist)'],
            'Software': ['Ashley Davis (Software Support)', 'Ryan Mitchell (Application Admin)', 'Samantha Lee (Software Engineer)'],
            'Database': ['Brian Kumar (Database Admin)', 'Linda Zhang (Data Engineer)', 'Carlos Mendez (DB Specialist)'],
            'Infrastructure': ['Mark Anderson (Infrastructure Lead)', 'Helen Wu (Cloud Architect)', 'Paul Johnson (Systems Engineer)'],
            'Cloud Services': ['Diana Chen (Cloud Engineer)', 'Jason Park (DevOps Lead)', 'Michelle Kim (Cloud Specialist)'],
            'Integration': ['Andrew Foster (Integration Specialist)', 'Stephanie Liu (API Developer)', 'Brandon Wong (Systems Integrator)'],
            'Monitoring': ['Tyler Brooks (Monitoring Engineer)', 'Kimberly Davis (Observability Lead)', 'Justin Chen (SRE)'],
            'Backup & Recovery': ['Laura Martinez (Backup Admin)', 'Matthew Taylor (Recovery Specialist)', 'Rachel Kim (Data Protection)'],
            'User Management': ['Amanda Wilson (User Admin)', 'Christopher Lee (Identity Manager)', 'Maria Rodriguez (Account Specialist)']
        }
        
        agents = agent_mapping.get(category, ['General Support Team'])
        recommended = random.choice(agents)
        
        # Add priority-based urgency note
        urgency_note = ""
        if priority == 'urgent':
            urgency_note = " (URGENT - Immediate assignment required)"
        elif priority == 'high':
            urgency_note = " (High priority - Assign within 1 hour)"
        
        return f"{recommended}{urgency_note}"
    
    def _get_availability_status(self) -> str:
        """Generate realistic availability status."""
        current_hour = datetime.now().hour
        
        # Business hours logic (9 AM - 6 PM)
        if 9 <= current_hour <= 18:
            statuses = [
                "✅ Multiple agents available - Standard response time expected",
                "🟡 Limited agents available - Slightly delayed response possible", 
                "✅ Full team coverage - Immediate assignment possible",
                "🟡 Peak hours - Normal queue processing",
                "✅ Agents standing by - Quick resolution expected"
            ]
            return random.choice(statuses)
        elif 6 < current_hour < 9 or 18 < current_hour < 22:
            # Extended hours
            statuses = [
                "🟡 Extended hours coverage - On-call team available",
                "⏰ Limited staff - Response within 2-4 hours",
                "🟡 Reduced capacity - Priority tickets handled first"
            ]
            return random.choice(statuses)
        else:
            # Night/weekend
            statuses = [
                "🌙 After-hours support - Emergency escalation available",
                "⏰ Night shift coverage - Response by next business day",
                "🚨 Emergency-only staffing - Urgent tickets escalated automatically"
            ]
            return random.choice(statuses)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of auto ticket generation."""
        uptime = None
        if self.start_time:
            uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        return {
            'is_running': self.is_running,
            'ticket_count': self.ticket_count,
            'start_time': self.start_time,
            'uptime_seconds': uptime,
            'uptime_minutes': uptime / 60 if uptime else None
        }


# Global instance
auto_ticket_generator = AutoTicketGenerator()
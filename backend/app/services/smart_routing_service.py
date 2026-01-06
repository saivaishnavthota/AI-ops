"""
Smart Routing Service for AI-first Service Desk.

Intelligently routes tickets and conversations to the best-suited agents
based on skills, workload, availability, and AI analysis.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from ..models.user import User, UserRole
from ..models.team import Team, TeamMember
from ..models.ticket import Ticket
from ..models.virtual_agent import Conversation, AgentPerformance
from ..ml.client import AnthropicClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AgentScore:
    """Agent scoring for routing decisions."""
    agent_id: UUID
    agent_name: str
    score: float
    reasoning: str
    availability: str
    current_workload: int
    skill_match: float
    performance_score: float


@dataclass
class RoutingRecommendation:
    """Routing recommendation result."""
    recommended_agent: Optional[AgentScore]
    alternative_agents: List[AgentScore]
    team_recommendation: Optional[str]
    escalation_needed: bool
    reasoning: str
    confidence: float


class SmartRoutingService:
    """
    AI-powered smart routing for tickets and conversations.
    
    Features:
    - Skill-based routing
    - Workload balancing
    - Performance-based assignment
    - SLA-aware routing
    - Learning from routing outcomes
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._client: Optional[AnthropicClient] = None

    async def __aenter__(self):
        if settings.ANTHROPIC_API_KEY:
            self._client = AnthropicClient()
            await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def route_ticket(
        self,
        ticket_id: UUID,
        priority_override: Optional[str] = None
    ) -> RoutingRecommendation:
        """
        Route a ticket to the best available agent.
        
        Args:
            ticket_id: ID of the ticket to route
            priority_override: Override ticket priority for routing
            
        Returns:
            RoutingRecommendation with agent suggestions
        """
        # Get ticket details
        result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        # Analyze ticket requirements
        requirements = await self._analyze_ticket_requirements(
            ticket,
            priority_override or ticket.priority
        )
        
        # Get available agents
        available_agents = await self._get_available_agents(
            ticket.organization_id,
            requirements["category"],
            requirements["skills_needed"]
        )
        
        # Score agents
        agent_scores = []
        for agent in available_agents:
            score = await self._score_agent_for_ticket(
                agent,
                ticket,
                requirements
            )
            agent_scores.append(score)
        
        # Sort by score
        agent_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Determine recommendation
        recommended_agent = agent_scores[0] if agent_scores else None
        alternative_agents = agent_scores[1:4] if len(agent_scores) > 1 else []
        
        # Check if escalation needed
        escalation_needed = (
            not recommended_agent or
            recommended_agent.score < 0.6 or
            requirements["priority"] == "urgent" and recommended_agent.current_workload > 5
        )
        
        # Get team recommendation
        team_recommendation = await self._get_team_recommendation(
            ticket.organization_id,
            requirements["category"]
        )
        
        return RoutingRecommendation(
            recommended_agent=recommended_agent,
            alternative_agents=alternative_agents,
            team_recommendation=team_recommendation,
            escalation_needed=escalation_needed,
            reasoning=self._generate_routing_reasoning(
                recommended_agent,
                requirements,
                escalation_needed
            ),
            confidence=recommended_agent.score if recommended_agent else 0.0
        )

    async def route_conversation(
        self,
        conversation_id: UUID
    ) -> RoutingRecommendation:
        """Route an escalated conversation to an agent."""
        
        # Get conversation details
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Convert conversation to ticket-like requirements
        requirements = {
            "category": conversation.category or "general",
            "priority": conversation.priority or "normal",
            "skills_needed": [conversation.intent] if conversation.intent else [],
            "urgency_score": self._calculate_urgency_score(
                conversation.priority or "normal",
                conversation.sentiment or "neutral"
            )
        }
        
        # Get available agents
        available_agents = await self._get_available_agents(
            conversation.organization_id,
            requirements["category"],
            requirements["skills_needed"]
        )
        
        # Score agents (simplified for conversations)
        agent_scores = []
        for agent in available_agents:
            score = await self._score_agent_for_conversation(
                agent,
                conversation,
                requirements
            )
            agent_scores.append(score)
        
        # Sort by score
        agent_scores.sort(key=lambda x: x.score, reverse=True)
        
        recommended_agent = agent_scores[0] if agent_scores else None
        alternative_agents = agent_scores[1:3] if len(agent_scores) > 1 else []
        
        return RoutingRecommendation(
            recommended_agent=recommended_agent,
            alternative_agents=alternative_agents,
            team_recommendation=None,
            escalation_needed=not recommended_agent,
            reasoning=f"Conversation routing based on intent: {conversation.intent}",
            confidence=recommended_agent.score if recommended_agent else 0.0
        )

    async def _analyze_ticket_requirements(
        self,
        ticket: Ticket,
        priority: str
    ) -> Dict[str, Any]:
        """Analyze what skills and expertise a ticket requires."""
        
        if self._client:
            return await self._ai_analyze_requirements(ticket, priority)
        else:
            return await self._rule_based_requirements(ticket, priority)

    async def _ai_analyze_requirements(
        self,
        ticket: Ticket,
        priority: str
    ) -> Dict[str, Any]:
        """Use AI to analyze ticket requirements."""
        
        system_prompt = """You are an expert IT service desk manager.

Analyze the ticket and determine what skills, expertise, and team would be best suited to handle it.

Consider:
1. Technical skills required
2. Domain expertise needed
3. Complexity level
4. Time sensitivity
5. Required permissions/access levels

Respond with JSON only."""

        user_prompt = f"""Analyze this support ticket:

Subject: {ticket.subject}
Description: {ticket.description}
Category: {ticket.category}
Priority: {priority}

Determine:
1. Required skills (e.g., ["windows_admin", "network_troubleshooting", "database"])
2. Complexity level (1-5 scale)
3. Estimated resolution time
4. Required team type
5. Urgency score (1-10)

Respond with JSON:
{{
    "skills_needed": ["skill1", "skill2"],
    "complexity": 3,
    "estimated_hours": 2,
    "team_type": "infrastructure",
    "urgency_score": 7,
    "category": "infrastructure",
    "requires_senior": false
}}"""

        try:
            response = await self._client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=400
            )
            
            result = response.get("analysis", {})
            return {
                "skills_needed": result.get("skills_needed", []),
                "complexity": result.get("complexity", 3),
                "estimated_hours": result.get("estimated_hours", 2),
                "team_type": result.get("team_type", "general"),
                "urgency_score": result.get("urgency_score", 5),
                "category": result.get("category", ticket.category),
                "requires_senior": result.get("requires_senior", False),
                "priority": priority
            }
        except Exception as e:
            logger.error(f"AI requirements analysis failed: {e}")
            return await self._rule_based_requirements(ticket, priority)

    async def _rule_based_requirements(
        self,
        ticket: Ticket,
        priority: str
    ) -> Dict[str, Any]:
        """Rule-based ticket requirements analysis."""
        
        subject_lower = ticket.subject.lower()
        description_lower = (ticket.description or "").lower()
        text = f"{subject_lower} {description_lower}"
        
        # Skill mapping
        skill_patterns = {
            "windows_admin": ["windows", "active directory", "domain", "gpo"],
            "linux_admin": ["linux", "ubuntu", "centos", "bash", "shell"],
            "network_troubleshooting": ["network", "connectivity", "vpn", "firewall", "dns"],
            "database": ["database", "sql", "mysql", "postgres", "oracle"],
            "application_support": ["application", "software", "app", "program"],
            "security": ["security", "virus", "malware", "breach", "unauthorized"],
            "hardware": ["hardware", "computer", "laptop", "printer", "monitor"],
            "email": ["email", "outlook", "exchange", "mail"],
            "backup_recovery": ["backup", "restore", "recovery", "data loss"]
        }
        
        skills_needed = []
        for skill, patterns in skill_patterns.items():
            if any(pattern in text for pattern in patterns):
                skills_needed.append(skill)
        
        # Complexity based on keywords
        complexity_indicators = {
            5: ["critical", "emergency", "outage", "down", "crashed"],
            4: ["error", "failed", "not working", "broken"],
            3: ["slow", "performance", "issue", "problem"],
            2: ["question", "how to", "help with"],
            1: ["request", "need", "want"]
        }
        
        complexity = 3  # Default
        for level, indicators in complexity_indicators.items():
            if any(indicator in text for indicator in indicators):
                complexity = level
                break
        
        # Urgency score
        urgency_score = self._calculate_urgency_score(priority, "neutral")
        
        # Team type based on category
        team_mapping = {
            "infrastructure": "infrastructure",
            "application": "devops",
            "security": "security",
            "network": "infrastructure",
            "database": "operations",
            "authentication": "security"
        }
        
        return {
            "skills_needed": skills_needed,
            "complexity": complexity,
            "estimated_hours": complexity,
            "team_type": team_mapping.get(ticket.category, "general"),
            "urgency_score": urgency_score,
            "category": ticket.category,
            "requires_senior": complexity >= 4 or priority in ["urgent", "high"],
            "priority": priority
        }

    def _calculate_urgency_score(self, priority: str, sentiment: str) -> int:
        """Calculate urgency score (1-10)."""
        
        priority_scores = {
            "urgent": 9,
            "high": 7,
            "normal": 5,
            "low": 3
        }
        
        sentiment_modifiers = {
            "negative": 2,
            "frustrated": 3,
            "neutral": 0,
            "positive": -1
        }
        
        base_score = priority_scores.get(priority, 5)
        modifier = sentiment_modifiers.get(sentiment, 0)
        
        return max(1, min(10, base_score + modifier))

    async def _get_available_agents(
        self,
        organization_id: UUID,
        category: str,
        skills_needed: List[str]
    ) -> List[User]:
        """Get available agents who can handle the request, prioritizing team members."""
        
        # First, try to get agents from category-specific teams
        team_agents = await self._get_team_agents_for_category(organization_id, category)
        
        if team_agents:
            # Filter to active agents with appropriate roles
            qualified_team_agents = [
                agent for agent in team_agents 
                if agent.is_active and agent.role in [UserRole.OPERATOR.value, UserRole.ADMIN.value]
            ]
            
            if qualified_team_agents:
                return qualified_team_agents
        
        # Fallback to all available agents if no team-specific agents found
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.organization_id == organization_id,
                    User.is_active == True,
                    User.role.in_([UserRole.OPERATOR.value, UserRole.ADMIN.value])
                )
            )
        )
        
        return result.scalars().all()

    async def _get_team_agents_for_category(
        self,
        organization_id: UUID,
        category: str
    ) -> List[User]:
        """Get agents from teams that match the ticket category."""
        
        # Category to team type mapping
        category_team_mapping = {
            "infrastructure": ["infrastructure", "devops"],
            "application": ["devops", "application"],
            "security": ["security"],
            "network": ["infrastructure", "network"],
            "database": ["operations", "database"],
            "authentication": ["security", "operations"],
            "access": ["security", "operations"],
            "hardware": ["infrastructure", "operations"],
            "email": ["operations", "infrastructure"],
            "general": ["operations", "devops"]
        }
        
        # Get team types for this category
        team_types = category_team_mapping.get(category.lower(), ["operations"])
        
        # Find teams that match these types
        teams_result = await self.db.execute(
            select(Team).where(
                and_(
                    Team.organization_id == organization_id,
                    Team.team_type.in_(team_types),
                    Team.is_active == True
                )
            )
        )
        teams = teams_result.scalars().all()
        
        if not teams:
            # Fallback: try to find teams by name matching
            name_patterns = {
                "infrastructure": ["infrastructure", "infra", "system"],
                "application": ["application", "app", "dev", "development"],
                "security": ["security", "sec"],
                "network": ["network", "net"],
                "database": ["database", "db", "data"],
                "authentication": ["security", "auth"],
                "access": ["security", "access"],
                "hardware": ["infrastructure", "hardware", "hw"],
                "email": ["operations", "ops", "email"],
                "general": ["operations", "support", "help"]
            }
            
            patterns = name_patterns.get(category.lower(), ["operations", "support"])
            
            # Search by team name containing these patterns
            name_conditions = []
            for pattern in patterns:
                name_conditions.append(Team.name.ilike(f"%{pattern}%"))
            
            if name_conditions:
                teams_result = await self.db.execute(
                    select(Team).where(
                        and_(
                            Team.organization_id == organization_id,
                            Team.is_active == True,
                            or_(*name_conditions)
                        )
                    )
                )
                teams = teams_result.scalars().all()
        
        if not teams:
            return []
        
        # Get team members from matching teams
        team_ids = [team.id for team in teams]
        members_result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id.in_(team_ids)
            )
        )
        members = members_result.scalars().all()
        
        if not members:
            return []
        
        # Get user objects for team members
        user_ids = [member.user_id for member in members]
        users_result = await self.db.execute(
            select(User).where(User.id.in_(user_ids))
        )
        
        return users_result.scalars().all()

    async def _score_agent_for_ticket(
        self,
        agent: User,
        ticket: Ticket,
        requirements: Dict[str, Any]
    ) -> AgentScore:
        """Score an agent's suitability for a ticket with enhanced team-based logic."""
        
        # Get agent's current workload
        workload_result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.assignee_id == agent.id,
                    Ticket.status.in_(["open", "in_progress"])
                )
            )
        )
        current_workload = workload_result.scalar() or 0
        
        # Get agent performance metrics
        performance_score = await self._get_agent_performance_score(agent.id)
        
        # Calculate team specialization bonus
        team_specialization_score = await self._calculate_team_specialization_score(
            agent, requirements["category"]
        )
        
        # Calculate skill match
        skill_match = await self._calculate_skill_match(
            agent,
            requirements["skills_needed"],
            requirements["category"]
        )
        
        # Calculate availability score
        availability_score = self._calculate_availability_score(current_workload)
        
        # Calculate priority match
        priority_match = self._calculate_priority_match(
            agent,
            requirements["priority"],
            requirements["complexity"]
        )
        
        # Enhanced scoring with team specialization
        total_score = (
            skill_match * 0.25 +
            availability_score * 0.25 +
            performance_score * 0.15 +
            priority_match * 0.10 +
            team_specialization_score * 0.25  # New: Team specialization bonus
        )
        
        reasoning = (
            f"Team specialization: {team_specialization_score:.2f}, "
            f"Skill match: {skill_match:.2f}, "
            f"Availability: {availability_score:.2f}, "
            f"Performance: {performance_score:.2f}"
        )
        
        return AgentScore(
            agent_id=agent.id,
            agent_name=agent.full_name,
            score=total_score,
            reasoning=reasoning,
            availability=self._get_availability_status(current_workload),
            current_workload=current_workload,
            skill_match=skill_match,
            performance_score=performance_score
        )

    async def _calculate_team_specialization_score(
        self,
        agent: User,
        category: str
    ) -> float:
        """Calculate bonus score based on agent's team specialization for the category."""
        
        # Get agent's team memberships
        memberships_result = await self.db.execute(
            select(TeamMember).where(TeamMember.user_id == agent.id)
        )
        memberships = memberships_result.scalars().all()
        
        if not memberships:
            return 0.5  # Default score for agents not in any team
        
        # Get teams for these memberships
        team_ids = [membership.team_id for membership in memberships]
        teams_result = await self.db.execute(
            select(Team).where(Team.id.in_(team_ids))
        )
        teams = teams_result.scalars().all()
        
        # Category to team specialization mapping
        specialization_mapping = {
            "infrastructure": {
                "infrastructure": 1.0,
                "devops": 0.8,
                "operations": 0.7,
                "security": 0.3
            },
            "application": {
                "devops": 1.0,
                "infrastructure": 0.6,
                "operations": 0.5,
                "security": 0.3
            },
            "security": {
                "security": 1.0,
                "operations": 0.4,
                "infrastructure": 0.3,
                "devops": 0.2
            },
            "network": {
                "infrastructure": 1.0,
                "devops": 0.6,
                "operations": 0.5,
                "security": 0.4
            },
            "database": {
                "operations": 1.0,
                "infrastructure": 0.7,
                "devops": 0.6,
                "security": 0.3
            },
            "authentication": {
                "security": 1.0,
                "operations": 0.7,
                "infrastructure": 0.4,
                "devops": 0.3
            },
            "access": {
                "security": 1.0,
                "operations": 0.8,
                "infrastructure": 0.4,
                "devops": 0.3
            },
            "hardware": {
                "infrastructure": 1.0,
                "operations": 0.8,
                "devops": 0.4,
                "security": 0.2
            },
            "email": {
                "operations": 1.0,
                "infrastructure": 0.7,
                "devops": 0.5,
                "security": 0.4
            }
        }
        
        category_mapping = specialization_mapping.get(category.lower(), {})
        
        # Calculate best specialization score from agent's teams
        best_score = 0.0
        best_team = None
        
        for team in teams:
            team_type = team.team_type.lower() if team.team_type else "general"
            
            # Direct team type match
            if team_type in category_mapping:
                score = category_mapping[team_type]
                if score > best_score:
                    best_score = score
                    best_team = team.name
            
            # Team name-based matching as fallback
            elif not best_score:
                team_name = team.name.lower()
                name_bonus = 0.0
                
                if category.lower() in team_name:
                    name_bonus = 0.9
                elif any(keyword in team_name for keyword in ["infrastructure", "infra"] if category.lower() == "infrastructure"):
                    name_bonus = 0.8
                elif any(keyword in team_name for keyword in ["security", "sec"] if category.lower() == "security"):
                    name_bonus = 0.8
                elif any(keyword in team_name for keyword in ["application", "app", "dev"] if category.lower() == "application"):
                    name_bonus = 0.8
                elif any(keyword in team_name for keyword in ["operations", "ops", "support"] if category.lower() in ["database", "email", "general"]):
                    name_bonus = 0.7
                
                if name_bonus > best_score:
                    best_score = name_bonus
                    best_team = team.name
        
        # Role-based bonus for team leads
        role_bonus = 0.0
        for membership in memberships:
            if membership.role == "lead":
                role_bonus = 0.1
                break
        
        final_score = min(1.0, best_score + role_bonus)
        
        return final_score if final_score > 0 else 0.5  # Minimum score for general agents

    async def _score_agent_for_conversation(
        self,
        agent: User,
        conversation: Conversation,
        requirements: Dict[str, Any]
    ) -> AgentScore:
        """Score an agent for handling an escalated conversation."""
        
        # Simplified scoring for conversations
        workload_result = await self.db.execute(
            select(func.count(Ticket.id)).where(
                and_(
                    Ticket.assignee_id == agent.id,
                    Ticket.status.in_(["open", "in_progress"])
                )
            )
        )
        current_workload = workload_result.scalar() or 0
        
        # Base score on availability and role
        availability_score = self._calculate_availability_score(current_workload)
        role_score = 0.9 if agent.role == UserRole.ADMIN.value else 0.7
        
        total_score = (availability_score * 0.6 + role_score * 0.4)
        
        return AgentScore(
            agent_id=agent.id,
            agent_name=agent.full_name,
            score=total_score,
            reasoning=f"Conversation escalation - Availability: {availability_score:.2f}",
            availability=self._get_availability_status(current_workload),
            current_workload=current_workload,
            skill_match=0.5,  # Default for conversations
            performance_score=0.7  # Default for conversations
        )

    async def _get_agent_performance_score(self, agent_id: UUID) -> float:
        """Get agent's performance score from recent metrics."""
        
        # Get recent performance data (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        result = await self.db.execute(
            select(AgentPerformance).where(
                and_(
                    AgentPerformance.agent_id == agent_id,
                    AgentPerformance.date >= thirty_days_ago
                )
            ).order_by(desc(AgentPerformance.date)).limit(30)
        )
        
        performance_records = result.scalars().all()
        
        if not performance_records:
            return 0.7  # Default score for new agents
        
        # Calculate average metrics
        avg_resolution_time = sum(p.avg_resolution_time_minutes for p in performance_records) / len(performance_records)
        avg_satisfaction = sum(p.customer_satisfaction_avg for p in performance_records) / len(performance_records)
        avg_fcr_rate = sum(p.first_contact_resolution_rate for p in performance_records) / len(performance_records)
        
        # Normalize scores (0-1 scale)
        resolution_score = max(0, min(1, 1 - (avg_resolution_time - 30) / 120))  # 30-150 min range
        satisfaction_score = avg_satisfaction / 5.0  # 1-5 scale
        fcr_score = avg_fcr_rate  # Already 0-1
        
        # Weighted average
        performance_score = (
            resolution_score * 0.4 +
            satisfaction_score * 0.4 +
            fcr_score * 0.2
        )
        
        return max(0.1, min(1.0, performance_score))

    async def _calculate_skill_match(
        self,
        agent: User,
        skills_needed: List[str],
        category: str
    ) -> float:
        """Calculate how well agent's skills match requirements."""
        
        if not skills_needed:
            return 0.7  # Default score when no specific skills needed
        
        # Get agent's skill scores from preferences or performance data
        agent_skills = agent.preferences.get("skills", {}) if agent.preferences else {}
        
        # Default skill levels based on role and category
        if not agent_skills:
            if agent.role == UserRole.ADMIN.value:
                agent_skills = {skill: 0.8 for skill in skills_needed}
            else:
                agent_skills = {skill: 0.6 for skill in skills_needed}
        
        # Calculate match score
        total_score = 0
        for skill in skills_needed:
            skill_level = agent_skills.get(skill, 0.3)  # Default low skill
            total_score += skill_level
        
        return min(1.0, total_score / len(skills_needed)) if skills_needed else 0.7

    def _calculate_availability_score(self, current_workload: int) -> float:
        """Calculate availability score based on current workload."""
        
        if current_workload == 0:
            return 1.0
        elif current_workload <= 3:
            return 0.8
        elif current_workload <= 6:
            return 0.6
        elif current_workload <= 10:
            return 0.4
        else:
            return 0.2

    def _calculate_priority_match(
        self,
        agent: User,
        priority: str,
        complexity: int
    ) -> float:
        """Calculate if agent is appropriate for priority/complexity."""
        
        # Admins can handle all priorities
        if agent.role == UserRole.ADMIN.value:
            return 1.0
        
        # Operators handle most tickets
        if priority in ["urgent", "high"] and complexity >= 4:
            return 0.7  # Operators can handle but may need escalation
        else:
            return 0.9

    def _get_availability_status(self, workload: int) -> str:
        """Get human-readable availability status."""
        
        if workload == 0:
            return "Available"
        elif workload <= 3:
            return "Light Load"
        elif workload <= 6:
            return "Moderate Load"
        elif workload <= 10:
            return "Heavy Load"
        else:
            return "Overloaded"

    async def _get_team_recommendation(
        self,
        organization_id: UUID,
        category: str
    ) -> Optional[str]:
        """Get team recommendation for category."""
        
        team_mapping = {
            "infrastructure": "Infrastructure Team",
            "application": "Application Support",
            "security": "Security Operations",
            "database": "Database Administration",
            "network": "Infrastructure Team"
        }
        
        return team_mapping.get(category)

    async def auto_assign_ticket_if_confident(
        self,
        ticket_id: UUID,
        confidence_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Automatically assign ticket if routing confidence is high enough.
        
        Args:
            ticket_id: ID of the ticket to potentially auto-assign
            confidence_threshold: Minimum confidence required for auto-assignment
            
        Returns:
            Dict with assignment result and details
        """
        
        # Get routing recommendation
        recommendation = await self.route_ticket(ticket_id)
        
        result = {
            "ticket_id": str(ticket_id),
            "auto_assigned": False,
            "confidence": recommendation.confidence,
            "threshold": confidence_threshold,
            "reasoning": recommendation.reasoning
        }
        
        # Check if we should auto-assign
        if (recommendation.recommended_agent and 
            recommendation.confidence >= confidence_threshold and
            not recommendation.escalation_needed and
            recommendation.recommended_agent.current_workload < 5):  # Don't overload agents
            
            # Perform auto-assignment
            success = await self.assign_ticket(
                ticket_id=ticket_id,
                agent_id=recommendation.recommended_agent.agent_id,
                assigned_by_id=None  # System assignment
            )
            
            if success:
                result.update({
                    "auto_assigned": True,
                    "assigned_agent": {
                        "id": str(recommendation.recommended_agent.agent_id),
                        "name": recommendation.recommended_agent.agent_name,
                        "score": recommendation.recommended_agent.score,
                        "availability": recommendation.recommended_agent.availability
                    }
                })
            else:
                result["error"] = "Assignment failed"
        else:
            # Explain why auto-assignment didn't happen
            reasons = []
            if not recommendation.recommended_agent:
                reasons.append("no suitable agent found")
            if recommendation.confidence < confidence_threshold:
                reasons.append(f"confidence too low ({recommendation.confidence:.2f} < {confidence_threshold})")
            if recommendation.escalation_needed:
                reasons.append("escalation required")
            if recommendation.recommended_agent and recommendation.recommended_agent.current_workload >= 5:
                reasons.append("agent workload too high")
            
            result["skip_reason"] = ", ".join(reasons)
        
        return result

    def _generate_routing_reasoning(
        self,
        recommended_agent: Optional[AgentScore],
        requirements: Dict[str, Any],
        escalation_needed: bool
    ) -> str:
        """Generate human-readable routing reasoning."""
        
        if escalation_needed:
            return "Escalation recommended due to high complexity or no suitable agents available"
        
        if not recommended_agent:
            return "No suitable agents found for this request"
        
        return (
            f"Recommended {recommended_agent.agent_name} based on "
            f"team specialization, skill match ({recommended_agent.skill_match:.1%}), "
            f"availability ({recommended_agent.availability}), "
            f"and performance history"
        )

    async def assign_ticket(
        self,
        ticket_id: UUID,
        agent_id: UUID,
        assigned_by_id: UUID
    ) -> bool:
        """Assign ticket to agent and update routing metrics."""
        
        # Get ticket and agent
        ticket_result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        ticket = ticket_result.scalar_one_or_none()
        
        agent_result = await self.db.execute(
            select(User).where(User.id == agent_id)
        )
        agent = agent_result.scalar_one_or_none()
        
        if not ticket or not agent:
            return False
        
        # Update ticket assignment
        ticket.assignee_id = agent_id
        ticket.assignee_name = agent.full_name
        ticket.status = "in_progress"
        
        # Add assignment comment
        assignment_comment = {
            "user": "System",
            "text": f"Ticket assigned to {agent.full_name}",
            "time": datetime.now(timezone.utc).isoformat()
        }
        
        if not ticket.comments:
            ticket.comments = []
        ticket.comments.append(assignment_comment)
        
        await self.db.commit()
        return True
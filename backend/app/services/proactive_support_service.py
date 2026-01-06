"""
Proactive Support Service for AI-first Service Desk.

Detects patterns, predicts issues, and provides proactive recommendations
to prevent problems before they become tickets.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text

from ..models.ticket import Ticket, KnowledgeBaseArticle
from ..models.alert import Alert
from ..models.incident import Incident
from ..models.user import User
from ..models.organization import Organization
from ..models.virtual_agent import Conversation
from ..ml.client import AnthropicClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysis:
    """Trend analysis result."""
    trend_type: str  # increasing, decreasing, stable, spike
    category: str
    description: str
    confidence: float
    impact_score: int  # 1-10
    recommended_actions: List[str]
    affected_users: int
    time_period: str


@dataclass
class ProactiveRecommendation:
    """Proactive support recommendation."""
    recommendation_id: str
    type: str  # kb_article, notification, automation, training
    title: str
    description: str
    priority: str
    target_audience: List[str]  # user_ids or "all_users"
    estimated_impact: str
    implementation_effort: str
    success_metrics: List[str]


@dataclass
class AnomalyDetection:
    """Anomaly detection result."""
    anomaly_type: str
    description: str
    severity: str
    affected_area: str
    detection_time: datetime
    confidence: float
    suggested_investigation: List[str]


class ProactiveSupportService:
    """
    AI-powered proactive support service.
    
    Features:
    - Trend analysis and pattern detection
    - Anomaly detection in support metrics
    - Proactive recommendations
    - Knowledge gap identification
    - Preventive action suggestions
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

    async def analyze_support_trends(
        self,
        organization_id: UUID,
        days_back: int = 30
    ) -> List[TrendAnalysis]:
        """Analyze support trends and identify patterns."""
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        # Get ticket trends by category
        ticket_trends = await self._analyze_ticket_trends(organization_id, start_date)
        
        # Get conversation trends
        conversation_trends = await self._analyze_conversation_trends(organization_id, start_date)
        
        # Get resolution time trends
        resolution_trends = await self._analyze_resolution_trends(organization_id, start_date)
        
        # Combine and analyze with AI
        all_trends = ticket_trends + conversation_trends + resolution_trends
        
        if self._client:
            enhanced_trends = await self._ai_enhance_trend_analysis(all_trends, organization_id)
            return enhanced_trends
        else:
            return all_trends

    async def _analyze_ticket_trends(
        self,
        organization_id: UUID,
        start_date: datetime
    ) -> List[TrendAnalysis]:
        """Analyze ticket volume and category trends."""
        
        # Get daily ticket counts by category
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE(created_at) as date,
                    category,
                    COUNT(*) as count
                FROM tickets 
                WHERE organization_id = :org_id 
                AND created_at >= :start_date
                GROUP BY DATE(created_at), category
                ORDER BY date, category
            """),
            {"org_id": str(organization_id), "start_date": start_date}
        )
        
        daily_counts = result.fetchall()
        
        # Group by category and analyze trends
        category_data = {}
        for row in daily_counts:
            category = row.category
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(row.count)
        
        trends = []
        for category, counts in category_data.items():
            if len(counts) >= 7:  # Need at least a week of data
                trend_analysis = self._calculate_trend(counts)
                
                trends.append(TrendAnalysis(
                    trend_type=trend_analysis["type"],
                    category=category,
                    description=f"Ticket volume for {category} category is {trend_analysis['type']}",
                    confidence=trend_analysis["confidence"],
                    impact_score=self._calculate_impact_score(trend_analysis, sum(counts)),
                    recommended_actions=self._get_trend_recommendations(category, trend_analysis),
                    affected_users=0,  # Will be calculated later
                    time_period=f"Last {len(counts)} days"
                ))
        
        return trends

    async def _analyze_conversation_trends(
        self,
        organization_id: UUID,
        start_date: datetime
    ) -> List[TrendAnalysis]:
        """Analyze virtual agent conversation trends."""
        
        # Get conversation metrics
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE(created_at) as date,
                    intent,
                    COUNT(*) as count,
                    AVG(CASE WHEN resolution_type = 'virtual_agent' THEN 1 ELSE 0 END) as auto_resolution_rate
                FROM conversations 
                WHERE organization_id = :org_id 
                AND created_at >= :start_date
                GROUP BY DATE(created_at), intent
                ORDER BY date, intent
            """),
            {"org_id": str(organization_id), "start_date": start_date}
        )
        
        conversation_data = result.fetchall()
        
        # Analyze auto-resolution trends
        intent_data = {}
        for row in conversation_data:
            intent = row.intent or "unknown"
            if intent not in intent_data:
                intent_data[intent] = {"counts": [], "resolution_rates": []}
            intent_data[intent]["counts"].append(row.count)
            intent_data[intent]["resolution_rates"].append(float(row.auto_resolution_rate or 0))
        
        trends = []
        for intent, data in intent_data.items():
            if len(data["counts"]) >= 5:
                # Analyze volume trend
                volume_trend = self._calculate_trend(data["counts"])
                
                # Analyze resolution rate trend
                resolution_trend = self._calculate_trend(data["resolution_rates"])
                
                if volume_trend["type"] == "increasing" and resolution_trend["type"] == "decreasing":
                    trends.append(TrendAnalysis(
                        trend_type="concerning",
                        category="virtual_agent",
                        description=f"Increasing {intent} requests with decreasing auto-resolution rate",
                        confidence=min(volume_trend["confidence"], resolution_trend["confidence"]),
                        impact_score=8,
                        recommended_actions=[
                            f"Review virtual agent knowledge for {intent}",
                            "Update response templates",
                            "Consider additional training data"
                        ],
                        affected_users=sum(data["counts"]),
                        time_period=f"Last {len(data['counts'])} days"
                    ))
        
        return trends

    async def _analyze_resolution_trends(
        self,
        organization_id: UUID,
        start_date: datetime
    ) -> List[TrendAnalysis]:
        """Analyze resolution time trends."""
        
        # Get resolution time data
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE(created_at) as date,
                    category,
                    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/3600) as avg_resolution_hours
                FROM tickets 
                WHERE organization_id = :org_id 
                AND created_at >= :start_date
                AND resolved_at IS NOT NULL
                GROUP BY DATE(created_at), category
                ORDER BY date, category
            """),
            {"org_id": str(organization_id), "start_date": start_date}
        )
        
        resolution_data = result.fetchall()
        
        # Group by category
        category_times = {}
        for row in resolution_data:
            category = row.category
            if category not in category_times:
                category_times[category] = []
            category_times[category].append(float(row.avg_resolution_hours or 0))
        
        trends = []
        for category, times in category_times.items():
            if len(times) >= 7:
                trend_analysis = self._calculate_trend(times)
                
                if trend_analysis["type"] == "increasing":
                    trends.append(TrendAnalysis(
                        trend_type="degrading",
                        category=category,
                        description=f"Resolution times for {category} tickets are increasing",
                        confidence=trend_analysis["confidence"],
                        impact_score=7,
                        recommended_actions=[
                            f"Review {category} resolution processes",
                            "Identify bottlenecks in workflow",
                            "Consider additional training or resources"
                        ],
                        affected_users=0,
                        time_period=f"Last {len(times)} days"
                    ))
        
        return trends

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and confidence."""
        
        if len(values) < 3:
            return {"type": "insufficient_data", "confidence": 0.0}
        
        # Simple linear regression slope
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        
        # Calculate confidence based on consistency
        avg_value = y_sum / n
        variance = sum((v - avg_value) ** 2 for v in values) / n
        confidence = min(1.0, abs(slope) / (variance + 0.1))
        
        # Determine trend type
        if abs(slope) < 0.1:
            trend_type = "stable"
        elif slope > 0.1:
            trend_type = "increasing"
        else:
            trend_type = "decreasing"
        
        # Check for spikes (sudden increases)
        if len(values) >= 5:
            recent_avg = sum(values[-3:]) / 3
            earlier_avg = sum(values[:-3]) / (len(values) - 3)
            if recent_avg > earlier_avg * 1.5:
                trend_type = "spike"
                confidence = min(1.0, confidence * 1.5)
        
        return {
            "type": trend_type,
            "confidence": confidence,
            "slope": slope
        }

    def _calculate_impact_score(self, trend_analysis: Dict[str, Any], volume: int) -> int:
        """Calculate impact score (1-10) based on trend and volume."""
        
        base_score = 5
        
        # Adjust for trend type
        if trend_analysis["type"] == "increasing":
            base_score += 2
        elif trend_analysis["type"] == "spike":
            base_score += 4
        elif trend_analysis["type"] == "decreasing":
            base_score -= 1
        
        # Adjust for volume
        if volume > 100:
            base_score += 2
        elif volume > 50:
            base_score += 1
        elif volume < 10:
            base_score -= 1
        
        # Adjust for confidence
        base_score = int(base_score * trend_analysis["confidence"])
        
        return max(1, min(10, base_score))

    def _get_trend_recommendations(self, category: str, trend_analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations based on trend analysis."""
        
        recommendations = []
        
        if trend_analysis["type"] == "increasing":
            recommendations.extend([
                f"Investigate root causes of increasing {category} tickets",
                f"Create or update knowledge base articles for {category}",
                f"Consider proactive notifications for {category} issues"
            ])
        elif trend_analysis["type"] == "spike":
            recommendations.extend([
                f"Immediate investigation of {category} spike required",
                f"Check for system-wide issues affecting {category}",
                f"Prepare proactive communication to users"
            ])
        
        return recommendations

    async def detect_anomalies(
        self,
        organization_id: UUID,
        hours_back: int = 24
    ) -> List[AnomalyDetection]:
        """Detect anomalies in support metrics."""
        
        start_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        anomalies = []
        
        # Check for ticket volume anomalies
        ticket_anomalies = await self._detect_ticket_anomalies(organization_id, start_time)
        anomalies.extend(ticket_anomalies)
        
        # Check for resolution time anomalies
        resolution_anomalies = await self._detect_resolution_anomalies(organization_id, start_time)
        anomalies.extend(resolution_anomalies)
        
        # Check for virtual agent performance anomalies
        agent_anomalies = await self._detect_agent_anomalies(organization_id, start_time)
        anomalies.extend(agent_anomalies)
        
        return anomalies

    async def _detect_ticket_anomalies(
        self,
        organization_id: UUID,
        start_time: datetime
    ) -> List[AnomalyDetection]:
        """Detect anomalies in ticket creation patterns."""
        
        # Get hourly ticket counts for the period
        result = await self.db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    COUNT(*) as count
                FROM tickets 
                WHERE organization_id = :org_id 
                AND created_at >= :start_time
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour
            """),
            {"org_id": str(organization_id), "start_time": start_time}
        )
        
        hourly_counts = [row.count for row in result.fetchall()]
        
        if len(hourly_counts) < 6:  # Need at least 6 hours of data
            return []
        
        # Calculate baseline (average of first 75% of data)
        baseline_size = int(len(hourly_counts) * 0.75)
        baseline_avg = sum(hourly_counts[:baseline_size]) / baseline_size
        baseline_std = (sum((x - baseline_avg) ** 2 for x in hourly_counts[:baseline_size]) / baseline_size) ** 0.5
        
        anomalies = []
        
        # Check recent hours for anomalies
        for i, count in enumerate(hourly_counts[baseline_size:], baseline_size):
            z_score = (count - baseline_avg) / (baseline_std + 1)  # Add 1 to avoid division by zero
            
            if abs(z_score) > 2:  # 2 standard deviations
                severity = "high" if abs(z_score) > 3 else "medium"
                anomaly_type = "ticket_spike" if z_score > 0 else "ticket_drop"
                
                anomalies.append(AnomalyDetection(
                    anomaly_type=anomaly_type,
                    description=f"Unusual ticket volume: {count} tickets (baseline: {baseline_avg:.1f})",
                    severity=severity,
                    affected_area="ticket_creation",
                    detection_time=datetime.now(timezone.utc),
                    confidence=min(1.0, abs(z_score) / 3),
                    suggested_investigation=[
                        "Check for system outages or incidents",
                        "Review recent changes or deployments",
                        "Analyze ticket categories for patterns"
                    ]
                ))
        
        return anomalies

    async def _detect_resolution_anomalies(
        self,
        organization_id: UUID,
        start_time: datetime
    ) -> List[AnomalyDetection]:
        """Detect anomalies in resolution times."""
        
        # Get recent resolution times
        result = await self.db.execute(
            text("""
                SELECT 
                    EXTRACT(EPOCH FROM (resolved_at - created_at))/3600 as resolution_hours
                FROM tickets 
                WHERE organization_id = :org_id 
                AND resolved_at >= :start_time
                AND resolved_at IS NOT NULL
            """),
            {"org_id": str(organization_id), "start_time": start_time}
        )
        
        resolution_times = [float(row.resolution_hours) for row in result.fetchall()]
        
        if len(resolution_times) < 5:
            return []
        
        # Calculate statistics
        avg_time = sum(resolution_times) / len(resolution_times)
        
        # Get historical baseline (last 30 days)
        historical_start = start_time - timedelta(days=30)
        historical_result = await self.db.execute(
            text("""
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (resolved_at - created_at))/3600) as avg_hours
                FROM tickets 
                WHERE organization_id = :org_id 
                AND resolved_at BETWEEN :hist_start AND :start_time
                AND resolved_at IS NOT NULL
            """),
            {"org_id": str(organization_id), "hist_start": historical_start, "start_time": start_time}
        )
        
        historical_avg = historical_result.scalar() or avg_time
        
        anomalies = []
        
        # Check if current average is significantly different
        if avg_time > historical_avg * 1.5:  # 50% increase
            anomalies.append(AnomalyDetection(
                anomaly_type="resolution_degradation",
                description=f"Resolution times increased: {avg_time:.1f}h vs {historical_avg:.1f}h baseline",
                severity="medium",
                affected_area="resolution_performance",
                detection_time=datetime.now(timezone.utc),
                confidence=0.8,
                suggested_investigation=[
                    "Check agent workload and availability",
                    "Review recent process changes",
                    "Analyze ticket complexity trends"
                ]
            ))
        
        return anomalies

    async def _detect_agent_anomalies(
        self,
        organization_id: UUID,
        start_time: datetime
    ) -> List[AnomalyDetection]:
        """Detect anomalies in virtual agent performance."""
        
        # Get virtual agent metrics
        result = await self.db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_conversations,
                    AVG(CASE WHEN resolution_type = 'virtual_agent' THEN 1 ELSE 0 END) as auto_resolution_rate,
                    AVG(confidence) as avg_confidence
                FROM conversations 
                WHERE organization_id = :org_id 
                AND created_at >= :start_time
            """),
            {"org_id": str(organization_id), "start_time": start_time}
        )
        
        metrics = result.fetchone()
        
        if not metrics or metrics.total_conversations < 5:
            return []
        
        anomalies = []
        
        # Check auto-resolution rate
        auto_resolution_rate = float(metrics.auto_resolution_rate or 0)
        if auto_resolution_rate < 0.3:  # Less than 30% auto-resolution
            anomalies.append(AnomalyDetection(
                anomaly_type="low_auto_resolution",
                description=f"Virtual agent auto-resolution rate dropped to {auto_resolution_rate:.1%}",
                severity="medium",
                affected_area="virtual_agent",
                detection_time=datetime.now(timezone.utc),
                confidence=0.9,
                suggested_investigation=[
                    "Review virtual agent knowledge base",
                    "Check for new types of requests",
                    "Update response templates"
                ]
            ))
        
        # Check confidence levels
        avg_confidence = float(metrics.avg_confidence or 0)
        if avg_confidence < 0.5:  # Low confidence
            anomalies.append(AnomalyDetection(
                anomaly_type="low_ai_confidence",
                description=f"Virtual agent confidence dropped to {avg_confidence:.1%}",
                severity="low",
                affected_area="virtual_agent",
                detection_time=datetime.now(timezone.utc),
                confidence=0.7,
                suggested_investigation=[
                    "Review unclear or ambiguous requests",
                    "Improve intent recognition training",
                    "Add more specific response patterns"
                ]
            ))
        
        return anomalies

    async def generate_proactive_recommendations(
        self,
        organization_id: UUID,
        trends: List[TrendAnalysis],
        anomalies: List[AnomalyDetection]
    ) -> List[ProactiveRecommendation]:
        """Generate proactive recommendations based on analysis."""
        
        recommendations = []
        
        # Knowledge base recommendations
        kb_recommendations = await self._generate_kb_recommendations(organization_id, trends)
        recommendations.extend(kb_recommendations)
        
        # Process improvement recommendations
        process_recommendations = await self._generate_process_recommendations(trends, anomalies)
        recommendations.extend(process_recommendations)
        
        # Training recommendations
        training_recommendations = await self._generate_training_recommendations(organization_id, trends)
        recommendations.extend(training_recommendations)
        
        # Automation recommendations
        automation_recommendations = await self._generate_automation_recommendations(trends)
        recommendations.extend(automation_recommendations)
        
        return recommendations

    async def _generate_kb_recommendations(
        self,
        organization_id: UUID,
        trends: List[TrendAnalysis]
    ) -> List[ProactiveRecommendation]:
        """Generate knowledge base article recommendations."""
        
        recommendations = []
        
        # Find categories with increasing trends but low KB coverage
        for trend in trends:
            if trend.trend_type == "increasing" and trend.impact_score >= 6:
                # Check KB coverage for this category
                kb_result = await self.db.execute(
                    select(func.count(KnowledgeBaseArticle.id)).where(
                        and_(
                            KnowledgeBaseArticle.organization_id == organization_id,
                            KnowledgeBaseArticle.category == trend.category,
                            KnowledgeBaseArticle.is_published == True
                        )
                    )
                )
                
                kb_count = kb_result.scalar() or 0
                
                if kb_count < 3:  # Low KB coverage
                    recommendations.append(ProactiveRecommendation(
                        recommendation_id=f"kb_{trend.category}_{int(datetime.now().timestamp())}",
                        type="kb_article",
                        title=f"Create Knowledge Base Articles for {trend.category.title()}",
                        description=f"Increasing {trend.category} tickets suggest need for self-service resources. Current KB has only {kb_count} articles.",
                        priority="high" if trend.impact_score >= 8 else "medium",
                        target_audience=["all_users"],
                        estimated_impact="Reduce ticket volume by 20-40%",
                        implementation_effort="Medium (2-4 hours)",
                        success_metrics=[
                            "Reduced ticket volume in category",
                            "Increased KB article views",
                            "Higher self-service resolution rate"
                        ]
                    ))
        
        return recommendations

    async def _generate_process_recommendations(
        self,
        trends: List[TrendAnalysis],
        anomalies: List[AnomalyDetection]
    ) -> List[ProactiveRecommendation]:
        """Generate process improvement recommendations."""
        
        recommendations = []
        
        # Check for resolution time issues
        resolution_issues = [t for t in trends if t.trend_type == "degrading"]
        if resolution_issues:
            recommendations.append(ProactiveRecommendation(
                recommendation_id=f"process_resolution_{int(datetime.now().timestamp())}",
                type="process_improvement",
                title="Optimize Resolution Processes",
                description="Resolution times are increasing across multiple categories. Process review recommended.",
                priority="high",
                target_audience=["support_agents", "managers"],
                estimated_impact="Improve resolution times by 15-25%",
                implementation_effort="High (1-2 weeks)",
                success_metrics=[
                    "Reduced average resolution time",
                    "Improved first-contact resolution rate",
                    "Higher customer satisfaction"
                ]
            ))
        
        # Check for volume spikes
        spike_issues = [a for a in anomalies if a.anomaly_type == "ticket_spike"]
        if spike_issues:
            recommendations.append(ProactiveRecommendation(
                recommendation_id=f"communication_{int(datetime.now().timestamp())}",
                type="notification",
                title="Proactive User Communication",
                description="Ticket spikes detected. Proactive communication may prevent additional tickets.",
                priority="urgent",
                target_audience=["all_users"],
                estimated_impact="Prevent 30-50% of related tickets",
                implementation_effort="Low (30 minutes)",
                success_metrics=[
                    "Reduced ticket volume",
                    "Faster issue awareness",
                    "Improved user satisfaction"
                ]
            ))
        
        return recommendations

    async def _generate_training_recommendations(
        self,
        organization_id: UUID,
        trends: List[TrendAnalysis]
    ) -> List[ProactiveRecommendation]:
        """Generate training recommendations."""
        
        recommendations = []
        
        # Check for categories with consistently high volume
        high_volume_categories = [t for t in trends if t.impact_score >= 7]
        
        if high_volume_categories:
            categories_str = ", ".join([t.category for t in high_volume_categories[:3]])
            recommendations.append(ProactiveRecommendation(
                recommendation_id=f"training_{int(datetime.now().timestamp())}",
                type="training",
                title=f"Agent Training for {categories_str}",
                description=f"High volume in {categories_str} suggests need for specialized training.",
                priority="medium",
                target_audience=["support_agents"],
                estimated_impact="Improve resolution efficiency by 20%",
                implementation_effort="Medium (4-8 hours)",
                success_metrics=[
                    "Faster resolution times",
                    "Higher first-contact resolution",
                    "Improved agent confidence"
                ]
            ))
        
        return recommendations

    async def _generate_automation_recommendations(
        self,
        trends: List[TrendAnalysis]
    ) -> List[ProactiveRecommendation]:
        """Generate automation recommendations."""
        
        recommendations = []
        
        # Look for repetitive patterns that could be automated
        repetitive_categories = [t for t in trends if t.trend_type in ["increasing", "stable"] and t.impact_score >= 5]
        
        for trend in repetitive_categories:
            if trend.category in ["password_reset", "account_unlock", "access_request"]:
                recommendations.append(ProactiveRecommendation(
                    recommendation_id=f"automation_{trend.category}_{int(datetime.now().timestamp())}",
                    type="automation",
                    title=f"Automate {trend.category.replace('_', ' ').title()} Process",
                    description=f"High volume of {trend.category} requests could be automated for faster resolution.",
                    priority="medium",
                    target_audience=["system_administrators"],
                    estimated_impact="Automate 60-80% of requests",
                    implementation_effort="High (1-3 weeks)",
                    success_metrics=[
                        "Reduced manual processing time",
                        "Faster user resolution",
                        "Freed agent capacity for complex issues"
                    ]
                ))
        
        return recommendations

    async def identify_knowledge_gaps(
        self,
        organization_id: UUID,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Identify gaps in knowledge base coverage."""
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        
        # Get ticket categories with high volume but low KB coverage
        result = await self.db.execute(
            text("""
                SELECT 
                    t.category,
                    COUNT(t.id) as ticket_count,
                    COALESCE(kb.article_count, 0) as kb_articles
                FROM tickets t
                LEFT JOIN (
                    SELECT category, COUNT(*) as article_count
                    FROM kb_articles 
                    WHERE organization_id = :org_id AND is_published = true
                    GROUP BY category
                ) kb ON t.category = kb.category
                WHERE t.organization_id = :org_id 
                AND t.created_at >= :start_date
                GROUP BY t.category, kb.article_count
                ORDER BY ticket_count DESC
            """),
            {"org_id": str(organization_id), "start_date": start_date}
        )
        
        gaps = []
        for row in result.fetchall():
            coverage_ratio = row.kb_articles / max(1, row.ticket_count / 10)  # 1 article per 10 tickets
            
            if coverage_ratio < 0.5:  # Less than 50% coverage
                gaps.append({
                    "category": row.category,
                    "ticket_count": row.ticket_count,
                    "kb_articles": row.kb_articles,
                    "coverage_ratio": coverage_ratio,
                    "priority": "high" if row.ticket_count > 20 else "medium",
                    "recommended_articles": max(1, row.ticket_count // 10)
                })
        
        return gaps
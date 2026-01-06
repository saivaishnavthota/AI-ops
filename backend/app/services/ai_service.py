from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from app.models import Alert

logger = logging.getLogger(__name__)


class AIService:
    """AI-powered service for alert correlation and analysis."""

    def __init__(self, db: Session):
        self.db = db
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )

    def find_similar_alerts(
        self, 
        alert: Alert, 
        threshold: float = 0.8,
        time_window_hours: int = 24
    ) -> List[Tuple[Alert, float]]:
        """
        Find similar alerts using AI-powered text similarity.
        
        Args:
            alert: The alert to find similarities for
            threshold: Minimum similarity score (0-1)
            time_window_hours: Time window to search within
            
        Returns:
            List of tuples (similar_alert, similarity_score)
        """
        try:
            # Get recent alerts from same organization
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            recent_alerts = self.db.query(Alert).filter(
                Alert.organization_id == alert.organization_id,
                Alert.created_at >= cutoff_time,
                Alert.id != alert.id,
                Alert.status.in_(["open", "firing", "acknowledged"])
            ).all()
            
            if not recent_alerts:
                return []
            
            # Prepare text for comparison
            alert_text = self._prepare_alert_text(alert)
            recent_texts = [self._prepare_alert_text(a) for a in recent_alerts]
            
            # Calculate similarity scores
            all_texts = [alert_text] + recent_texts
            
            try:
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            except Exception as e:
                logger.warning(f"TF-IDF similarity failed, using fallback: {e}")
                # Fallback to simple text matching
                similarities = np.array([
                    self._simple_text_similarity(alert_text, text) 
                    for text in recent_texts
                ])
            
            # Filter by threshold and return
            similar_alerts = []
            for i, similarity_score in enumerate(similarities):
                if similarity_score >= threshold:
                    similar_alerts.append((recent_alerts[i], float(similarity_score)))
            
            # Sort by similarity score descending
            similar_alerts.sort(key=lambda x: x[1], reverse=True)
            
            return similar_alerts
            
        except Exception as e:
            logger.error(f"Error finding similar alerts: {e}")
            return []

    def _prepare_alert_text(self, alert: Alert) -> str:
        """Prepare alert text for similarity comparison."""
        parts = []
        
        if alert.title:
            parts.append(alert.title)
        if alert.description:
            parts.append(alert.description)
        elif alert.message:
            parts.append(alert.message)
        if alert.service:
            parts.append(f"service:{alert.service}")
        if alert.host:
            parts.append(f"host:{alert.host}")
        if alert.environment:
            parts.append(f"env:{alert.environment}")
        
        # Add tags
        if alert.tags:
            for key, value in alert.tags.items():
                parts.append(f"{key}:{value}")
        
        return " ".join(parts)

    def _simple_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity fallback using word overlap."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

    def correlate_alerts_by_pattern(
        self, 
        alerts: List[Alert]
    ) -> Dict[str, List[Alert]]:
        """
        Group alerts by detected patterns.
        
        Returns:
            Dictionary mapping pattern names to lists of alerts
        """
        patterns = {}
        
        # Pattern 1: Same service + environment
        service_env_groups = {}
        for alert in alerts:
            key = f"{alert.service}_{alert.environment}"
            if key not in service_env_groups:
                service_env_groups[key] = []
            service_env_groups[key].append(alert)
        
        for key, group_alerts in service_env_groups.items():
            if len(group_alerts) > 1:
                patterns[f"service_env_{key}"] = group_alerts
        
        # Pattern 2: Same host
        host_groups = {}
        for alert in alerts:
            if alert.host:
                if alert.host not in host_groups:
                    host_groups[alert.host] = []
                host_groups[alert.host].append(alert)
        
        for host, group_alerts in host_groups.items():
            if len(group_alerts) > 1:
                patterns[f"host_{host}"] = group_alerts
        
        # Pattern 3: Cascading failures (temporal)
        time_sorted = sorted(alerts, key=lambda a: a.created_at)
        cascading = []
        for i in range(len(time_sorted) - 1):
            time_diff = (time_sorted[i + 1].created_at - time_sorted[i].created_at).total_seconds()
            if time_diff < 300:  # Within 5 minutes
                if time_sorted[i] not in cascading:
                    cascading.append(time_sorted[i])
                cascading.append(time_sorted[i + 1])
        
        if len(cascading) > 1:
            patterns["cascading_failure"] = cascading
        
        return patterns

    def predict_alert_severity(self, alert: Alert) -> str:
        """
        Predict alert severity based on historical patterns.
        
        This is a simplified version - in production, you'd use a trained ML model.
        """
        # Get similar historical alerts
        similar_alerts = self.find_similar_alerts(alert, threshold=0.7, time_window_hours=168)  # 1 week
        
        if not similar_alerts:
            return alert.severity
        
        # Count severity levels
        severity_counts = {}
        for similar_alert, _ in similar_alerts:
            sev = similar_alert.severity
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Return most common severity
        if severity_counts:
            return max(severity_counts.items(), key=lambda x: x[1])[0]
        
        return alert.severity

    def detect_alert_anomalies(
        self, 
        organization_id: str,
        time_window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in alert patterns.
        
        Returns:
            List of detected anomalies with details
        """
        anomalies = []
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Get recent alerts
        recent_alerts = self.db.query(Alert).filter(
            Alert.organization_id == organization_id,
            Alert.created_at >= cutoff_time
        ).all()
        
        if len(recent_alerts) < 10:
            return anomalies
        
        # Anomaly 1: Sudden spike in alerts
        alerts_per_hour = {}
        for alert in recent_alerts:
            hour = alert.created_at.replace(minute=0, second=0, microsecond=0)
            alerts_per_hour[hour] = alerts_per_hour.get(hour, 0) + 1
        
        if alerts_per_hour:
            avg_per_hour = np.mean(list(alerts_per_hour.values()))
            std_per_hour = np.std(list(alerts_per_hour.values()))
            
            for hour, count in alerts_per_hour.items():
                if count > avg_per_hour + (2 * std_per_hour):
                    anomalies.append({
                        "type": "alert_spike",
                        "timestamp": hour,
                        "count": count,
                        "average": avg_per_hour,
                        "description": f"Alert spike detected: {count} alerts (avg: {avg_per_hour:.1f})"
                    })
        
        # Anomaly 2: New alert sources
        historical_sources = set(
            self.db.query(Alert.source).filter(
                Alert.organization_id == organization_id,
                Alert.created_at < cutoff_time
            ).distinct().all()
        )
        
        recent_sources = set(alert.source for alert in recent_alerts)
        new_sources = recent_sources - {s[0] for s in historical_sources}
        
        if new_sources:
            anomalies.append({
                "type": "new_alert_source",
                "sources": list(new_sources),
                "description": f"New alert sources detected: {', '.join(new_sources)}"
            })
        
        return anomalies

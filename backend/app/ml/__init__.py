"""
AI/ML Module for AI-Ops Platform

This module provides AI-powered capabilities powered by Anthropic Claude:
- Incident classification
- Resolution suggestions
- Alert correlation
- Anomaly detection
- Predictive analytics
"""

from .client import AnthropicClient, MistralClient  # MistralClient is alias for backward compatibility
from .classifier import IncidentClassifier, ClassificationResult
from .suggester import ResolutionSuggester, ResolutionSuggestion
from .correlator import AlertCorrelator, AlertInfo, CorrelationResult, CorrelationGroup
from .service import AIService, get_ai_service

__all__ = [
    "AnthropicClient",
    "MistralClient",  # Backward compatibility alias
    "IncidentClassifier",
    "ClassificationResult",
    "ResolutionSuggester",
    "ResolutionSuggestion",
    "AlertCorrelator",
    "AlertInfo",
    "CorrelationResult",
    "CorrelationGroup",
    "AIService",
    "get_ai_service",
]

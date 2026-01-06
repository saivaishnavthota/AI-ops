"""
Virtual Agent Service for AI-first Service Desk.

Handles intelligent conversation processing, intent recognition,
automated responses, and smart routing decisions.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ..models.virtual_agent import (
    Conversation, ConversationMessage, VirtualAgentKnowledge,
    ConversationStatus, MessageType, ResolutionType
)
from ..models.ticket import Ticket, KnowledgeBaseArticle
from ..models.user import User
from ..ml.client import AnthropicClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent recognition."""
    intent: str
    confidence: float
    category: str
    priority: str
    sentiment: str
    keywords: List[str]
    suggested_actions: List[str]


@dataclass
class ResponseSuggestion:
    """AI-generated response suggestion."""
    content: str
    confidence: float
    kb_articles: List[str]
    actions: List[str]
    escalate: bool
    reasoning: str


class VirtualAgentService:
    """
    AI-powered virtual agent for service desk automation.
    
    Capabilities:
    - Intent recognition and classification
    - Automated response generation
    - Knowledge base integration
    - Smart routing and escalation
    - Learning from interactions
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

    async def process_message(
        self,
        conversation_id: UUID,
        message_content: str,
        user_id: Optional[UUID] = None,
        user_name: str = "Anonymous"
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate AI response.
        
        Returns:
            Dict containing response, actions, and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        # Get conversation
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Save user message
        user_message = ConversationMessage(
            conversation_id=conversation_id,
            message_type=MessageType.USER.value,
            content=message_content,
            sender_id=user_id,
            sender_name=user_name,
            processed_by_ai=False,
        )
        self.db.add(user_message)
        await self.db.flush()

        # Analyze intent and generate response
        intent_result = await self._analyze_intent(
            message_content, 
            conversation.organization_id,
            conversation_history=await self._get_conversation_history(conversation_id)
        )
        
        response_suggestion = await self._generate_response(
            message_content,
            intent_result,
            conversation.organization_id,
            conversation_history=await self._get_conversation_history(conversation_id)
        )

        # Update conversation with AI analysis
        conversation.intent = intent_result.intent
        conversation.sentiment = intent_result.sentiment
        conversation.confidence = intent_result.confidence
        conversation.category = intent_result.category
        conversation.priority = intent_result.priority

        # Create AI response message
        response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        ai_message = ConversationMessage(
            conversation_id=conversation_id,
            message_type=MessageType.AGENT.value,
            content=response_suggestion.content,
            sender_name="AI Assistant",
            processed_by_ai=True,
            ai_confidence=response_suggestion.confidence,
            ai_suggestions=[response_suggestion.content],
            response_time_ms=response_time_ms,
            kb_articles_referenced=response_suggestion.kb_articles,
            actions_taken=response_suggestion.actions,
        )
        self.db.add(ai_message)

        # Handle escalation if needed
        escalated = False
        if response_suggestion.escalate or intent_result.confidence < 0.6:
            await self._escalate_conversation(conversation, intent_result)
            escalated = True

        # Execute automated actions
        actions_executed = []
        if not escalated and response_suggestion.actions:
            actions_executed = await self._execute_actions(
                response_suggestion.actions,
                conversation,
                user_id
            )

        await self.db.commit()

        return {
            "response": response_suggestion.content,
            "confidence": response_suggestion.confidence,
            "intent": intent_result.intent,
            "sentiment": intent_result.sentiment,
            "category": intent_result.category,
            "priority": intent_result.priority,
            "kb_articles": response_suggestion.kb_articles,
            "actions_executed": actions_executed,
            "escalated": escalated,
            "response_time_ms": response_time_ms,
        }

    async def _analyze_intent(
        self,
        message: str,
        organization_id: UUID,
        conversation_history: List[Dict[str, Any]] = None
    ) -> IntentResult:
        """Analyze message intent using AI or rule-based fallback."""
        
        if self._client:
            return await self._ai_analyze_intent(message, organization_id, conversation_history)
        else:
            return await self._rule_based_intent_analysis(message, organization_id)

    async def _ai_analyze_intent(
        self,
        message: str,
        organization_id: UUID,
        conversation_history: List[Dict[str, Any]] = None
    ) -> IntentResult:
        """Use AI to analyze intent."""
        
        # Get organization-specific knowledge
        knowledge_result = await self.db.execute(
            select(VirtualAgentKnowledge).where(
                VirtualAgentKnowledge.organization_id == organization_id
            )
        )
        knowledge_entries = knowledge_result.scalars().all()
        
        # Build context for AI
        context = {
            "message": message,
            "conversation_history": conversation_history or [],
            "organization_intents": [
                {
                    "intent": k.intent,
                    "category": k.category,
                    "keywords": k.keywords,
                    "can_auto_resolve": k.can_auto_resolve
                }
                for k in knowledge_entries
            ]
        }

        system_prompt = """You are an expert virtual agent for IT service desk support.

Analyze the user's message and determine:
1. Intent (what they want to accomplish)
2. Category (infrastructure, application, security, access, etc.)
3. Priority (urgent, high, normal, low)
4. Sentiment (positive, neutral, negative, frustrated)
5. Confidence in your analysis (0.0-1.0)
6. Key keywords from the message
7. Suggested actions to resolve the issue

Common intents:
- password_reset: User needs password reset
- account_unlock: Account is locked
- access_request: Requesting access to systems/applications
- software_install: Need software installation
- hardware_issue: Hardware problems
- network_issue: Connectivity problems
- application_error: Application not working
- general_inquiry: General questions
- complaint: User complaint or escalation

Respond with JSON only."""

        user_prompt = f"""Analyze this support request:

Message: "{message}"

Organization-specific intents available: {[k['intent'] for k in context['organization_intents']]}

Conversation history: {context['conversation_history'][-3:] if context['conversation_history'] else 'None'}

Respond with JSON:
{{
    "intent": "specific_intent_name",
    "confidence": 0.85,
    "category": "category_name",
    "priority": "normal",
    "sentiment": "neutral",
    "keywords": ["keyword1", "keyword2"],
    "suggested_actions": ["action1", "action2"]
}}"""

        try:
            response = await self._client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=500
            )
            
            result_data = response.get("analysis", {})
            return IntentResult(
                intent=result_data.get("intent", "general_inquiry"),
                confidence=result_data.get("confidence", 0.5),
                category=result_data.get("category", "general"),
                priority=result_data.get("priority", "normal"),
                sentiment=result_data.get("sentiment", "neutral"),
                keywords=result_data.get("keywords", []),
                suggested_actions=result_data.get("suggested_actions", [])
            )
        except Exception as e:
            logger.error(f"AI intent analysis failed: {e}")
            return await self._rule_based_intent_analysis(message, organization_id)

    async def _rule_based_intent_analysis(
        self,
        message: str,
        organization_id: UUID
    ) -> IntentResult:
        """Fallback rule-based intent analysis."""
        
        message_lower = message.lower()
        
        # Intent patterns
        intent_patterns = {
            "password_reset": [
                r"password.*reset", r"forgot.*password", r"can't.*log.*in",
                r"password.*expired", r"reset.*password", r"password.*change"
            ],
            "account_unlock": [
                r"account.*locked", r"locked.*out", r"unlock.*account",
                r"can't.*access", r"account.*disabled"
            ],
            "access_request": [
                r"need.*access", r"request.*access", r"permission.*to",
                r"can.*i.*access", r"access.*to.*system"
            ],
            "software_install": [
                r"install.*software", r"need.*application", r"software.*request",
                r"install.*program", r"need.*tool"
            ],
            "hardware_issue": [
                r"computer.*not.*working", r"laptop.*problem", r"hardware.*issue",
                r"screen.*broken", r"keyboard.*not", r"mouse.*not"
            ],
            "network_issue": [
                r"internet.*not.*working", r"network.*down", r"can't.*connect",
                r"wifi.*problem", r"connection.*issue"
            ],
            "application_error": [
                r"application.*error", r"software.*not.*working", r"app.*crashed",
                r"error.*message", r"system.*error"
            ]
        }
        
        # Priority patterns
        priority_patterns = {
            "urgent": [r"urgent", r"asap", r"immediately", r"critical", r"emergency"],
            "high": [r"important", r"soon", r"quickly", r"high.*priority"],
            "low": [r"when.*convenient", r"no.*rush", r"low.*priority"]
        }
        
        # Sentiment patterns
        sentiment_patterns = {
            "negative": [r"frustrated", r"angry", r"terrible", r"awful", r"hate"],
            "positive": [r"thank", r"appreciate", r"great", r"excellent", r"love"]
        }
        
        # Analyze intent
        detected_intent = "general_inquiry"
        confidence = 0.3
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_intent = intent
                    confidence = 0.8
                    break
            if confidence > 0.5:
                break
        
        # Analyze priority
        priority = "normal"
        for pri, patterns in priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    priority = pri
                    break
        
        # Analyze sentiment
        sentiment = "neutral"
        for sent, patterns in sentiment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    sentiment = sent
                    break
        
        # Extract keywords
        keywords = []
        for word in message_lower.split():
            if len(word) > 3 and word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'who', 'oil', 'sit', 'set']:
                keywords.append(word)
        
        return IntentResult(
            intent=detected_intent,
            confidence=confidence,
            category=self._intent_to_category(detected_intent),
            priority=priority,
            sentiment=sentiment,
            keywords=keywords[:5],  # Top 5 keywords
            suggested_actions=self._get_suggested_actions(detected_intent)
        )

    def _intent_to_category(self, intent: str) -> str:
        """Map intent to category."""
        mapping = {
            "password_reset": "authentication",
            "account_unlock": "authentication",
            "access_request": "access",
            "software_install": "application",
            "hardware_issue": "infrastructure",
            "network_issue": "network",
            "application_error": "application",
            "general_inquiry": "general"
        }
        return mapping.get(intent, "general")

    def _get_suggested_actions(self, intent: str) -> List[str]:
        """Get suggested actions for intent."""
        actions = {
            "password_reset": ["send_password_reset_link", "verify_identity"],
            "account_unlock": ["unlock_account", "verify_identity"],
            "access_request": ["check_permissions", "create_access_request"],
            "software_install": ["check_software_catalog", "create_install_request"],
            "hardware_issue": ["create_hardware_ticket", "schedule_technician"],
            "network_issue": ["check_network_status", "run_diagnostics"],
            "application_error": ["check_application_status", "gather_error_details"],
            "general_inquiry": ["search_knowledge_base", "provide_general_help"]
        }
        return actions.get(intent, ["escalate_to_human"])

    async def _generate_response(
        self,
        message: str,
        intent_result: IntentResult,
        organization_id: UUID,
        conversation_history: List[Dict[str, Any]] = None
    ) -> ResponseSuggestion:
        """Generate AI response based on intent analysis."""
        
        if self._client:
            return await self._ai_generate_response(message, intent_result, organization_id, conversation_history)
        else:
            return await self._template_based_response(intent_result, organization_id)

    async def _ai_generate_response(
        self,
        message: str,
        intent_result: IntentResult,
        organization_id: UUID,
        conversation_history: List[Dict[str, Any]] = None
    ) -> ResponseSuggestion:
        """Use AI to generate personalized response."""
        
        # Get relevant KB articles
        kb_articles = await self._find_relevant_kb_articles(
            intent_result.keywords,
            intent_result.category,
            organization_id
        )
        
        # Get organization knowledge
        knowledge_result = await self.db.execute(
            select(VirtualAgentKnowledge).where(
                and_(
                    VirtualAgentKnowledge.organization_id == organization_id,
                    VirtualAgentKnowledge.intent == intent_result.intent
                )
            )
        )
        knowledge = knowledge_result.scalar_one_or_none()

        system_prompt = """You are a helpful IT support virtual agent. 

Generate a professional, empathetic response that:
1. Acknowledges the user's issue
2. Provides clear next steps
3. References relevant knowledge base articles if available
4. Maintains a helpful, professional tone
5. Determines if human escalation is needed

Guidelines:
- Be concise but thorough
- Use simple, non-technical language when possible
- Show empathy for user frustration
- Provide specific actionable steps
- Reference KB articles by ID when relevant

Respond with JSON only."""

        kb_context = ""
        if kb_articles:
            kb_context = f"\nRelevant KB articles available:\n"
            for article in kb_articles[:3]:  # Top 3 articles
                kb_context += f"- Article {article['id']}: {article['title']}\n"

        template_context = ""
        if knowledge:
            template_context = f"\nOrganization template: {knowledge.response_template}"

        user_prompt = f"""Generate a response for this support request:

User message: "{message}"
Intent: {intent_result.intent}
Category: {intent_result.category}
Priority: {intent_result.priority}
Sentiment: {intent_result.sentiment}
Confidence: {intent_result.confidence}

{kb_context}
{template_context}

Conversation history: {conversation_history[-2:] if conversation_history else 'None'}

Respond with JSON:
{{
    "content": "Your helpful response here",
    "confidence": 0.85,
    "kb_articles": ["article_id1", "article_id2"],
    "actions": ["action1", "action2"],
    "escalate": false,
    "reasoning": "Why this response was chosen"
}}"""

        try:
            response = await self._client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=800
            )
            
            result_data = response.get("response", {})
            return ResponseSuggestion(
                content=result_data.get("content", "I understand your request. Let me help you with that."),
                confidence=result_data.get("confidence", 0.7),
                kb_articles=result_data.get("kb_articles", []),
                actions=result_data.get("actions", []),
                escalate=result_data.get("escalate", False),
                reasoning=result_data.get("reasoning", "AI-generated response")
            )
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return await self._template_based_response(intent_result, organization_id)

    async def _template_based_response(
        self,
        intent_result: IntentResult,
        organization_id: UUID
    ) -> ResponseSuggestion:
        """Generate response using templates."""
        
        # Get organization-specific template
        knowledge_result = await self.db.execute(
            select(VirtualAgentKnowledge).where(
                and_(
                    VirtualAgentKnowledge.organization_id == organization_id,
                    VirtualAgentKnowledge.intent == intent_result.intent
                )
            )
        )
        knowledge = knowledge_result.scalar_one_or_none()
        
        if knowledge:
            content = knowledge.response_template
            actions = knowledge.required_actions or []
            escalate = knowledge.requires_approval
        else:
            # Default templates
            templates = {
                "password_reset": "I can help you reset your password. I'll send you a password reset link to your registered email address. Please check your email and follow the instructions.",
                "account_unlock": "I see your account is locked. I can unlock it for you right away. Your account should be accessible within a few minutes.",
                "access_request": "I understand you need access to a system or application. I'll create an access request for you. Could you please specify which system you need access to?",
                "software_install": "I can help you with software installation. Let me check our software catalog and create an installation request for you.",
                "hardware_issue": "I'm sorry to hear you're having hardware problems. I'll create a support ticket and schedule a technician to assist you.",
                "network_issue": "I understand you're experiencing network connectivity issues. Let me run some diagnostics and check the network status for you.",
                "application_error": "I see you're having trouble with an application. Let me check the application status and gather some details about the error you're experiencing.",
                "general_inquiry": "Thank you for contacting support. I'm here to help you. Could you please provide more details about what you need assistance with?"
            }
            
            content = templates.get(intent_result.intent, templates["general_inquiry"])
            actions = intent_result.suggested_actions
            escalate = intent_result.confidence < 0.6
        
        return ResponseSuggestion(
            content=content,
            confidence=0.8 if knowledge else 0.6,
            kb_articles=[],
            actions=actions,
            escalate=escalate,
            reasoning="Template-based response"
        )

    async def _find_relevant_kb_articles(
        self,
        keywords: List[str],
        category: str,
        organization_id: UUID,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find relevant knowledge base articles."""
        
        if not keywords:
            return []
        
        # Search by keywords and category
        search_terms = " | ".join(keywords)
        
        result = await self.db.execute(
            select(KnowledgeBaseArticle).where(
                and_(
                    KnowledgeBaseArticle.organization_id == organization_id,
                    KnowledgeBaseArticle.is_published == True,
                    or_(
                        KnowledgeBaseArticle.title.ilike(f"%{search_terms}%"),
                        KnowledgeBaseArticle.content.ilike(f"%{search_terms}%"),
                        KnowledgeBaseArticle.category == category
                    )
                )
            ).order_by(KnowledgeBaseArticle.helpful_count.desc()).limit(limit)
        )
        
        articles = result.scalars().all()
        return [
            {
                "id": str(article.id),
                "title": article.title,
                "excerpt": article.excerpt,
                "category": article.category,
                "helpful_count": article.helpful_count
            }
            for article in articles
        ]

    async def _get_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get conversation message history."""
        
        result = await self.db.execute(
            select(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation_id
            ).order_by(ConversationMessage.created_at.desc()).limit(limit)
        )
        
        messages = result.scalars().all()
        return [
            {
                "type": msg.message_type,
                "content": msg.content,
                "sender": msg.sender_name,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in reversed(messages)  # Reverse to get chronological order
        ]

    async def _escalate_conversation(
        self,
        conversation: Conversation,
        intent_result: IntentResult
    ) -> None:
        """Escalate conversation to human agent."""
        
        conversation.status = ConversationStatus.ESCALATED.value
        
        # Create a ticket for human follow-up
        ticket = Ticket(
            organization_id=conversation.organization_id,
            subject=f"Escalated: {conversation.subject}",
            description=f"Virtual agent escalation - Intent: {intent_result.intent}, Confidence: {intent_result.confidence}",
            status="open",
            priority=intent_result.priority,
            category=intent_result.category,
            requester_id=conversation.user_id,
            requester_name=conversation.user_name,
            comments=[]
        )
        
        self.db.add(ticket)
        await self.db.flush()
        
        conversation.ticket_id = ticket.id

    async def _execute_actions(
        self,
        actions: List[str],
        conversation: Conversation,
        user_id: Optional[UUID]
    ) -> List[str]:
        """Execute automated actions."""
        
        executed = []
        
        for action in actions:
            try:
                if action == "send_password_reset_link":
                    # In a real implementation, this would integrate with identity provider
                    executed.append("password_reset_email_sent")
                    
                elif action == "unlock_account":
                    # In a real implementation, this would integrate with identity provider
                    executed.append("account_unlocked")
                    
                elif action == "search_knowledge_base":
                    # Already handled in response generation
                    executed.append("kb_search_completed")
                    
                # Add more automated actions as needed
                
            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")
        
        return executed

    async def create_conversation(
        self,
        organization_id: UUID,
        user_id: Optional[UUID],
        user_name: str,
        user_email: Optional[str],
        subject: str,
        initial_message: str
    ) -> UUID:
        """Create a new conversation."""
        
        conversation = Conversation(
            organization_id=organization_id,
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            subject=subject,
            status=ConversationStatus.ACTIVE.value,
            metadata={}
        )
        
        self.db.add(conversation)
        await self.db.flush()
        
        # Process initial message
        await self.process_message(
            conversation.id,
            initial_message,
            user_id,
            user_name
        )
        
        return conversation.id

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all messages in a conversation."""
        
        result = await self.db.execute(
            select(ConversationMessage).where(
                ConversationMessage.conversation_id == conversation_id
            ).order_by(ConversationMessage.created_at).limit(limit)
        )
        
        messages = result.scalars().all()
        return [
            {
                "id": str(msg.id),
                "type": msg.message_type,
                "content": msg.content,
                "sender_name": msg.sender_name,
                "timestamp": msg.created_at.isoformat(),
                "ai_confidence": msg.ai_confidence,
                "kb_articles": msg.kb_articles_referenced,
                "actions": msg.actions_taken
            }
            for msg in messages
        ]
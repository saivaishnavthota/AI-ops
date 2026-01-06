#!/usr/bin/env python3
"""
Seed Virtual Agent Knowledge Base for AI-first Service Desk.
"""
import sys
import os
import asyncio
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal
from app.models import Organization, VirtualAgentKnowledge


async def seed_virtual_agent_knowledge(db: AsyncSession, org_id: str):
    """Seed virtual agent knowledge base."""
    print("Seeding virtual agent knowledge base...")
    
    knowledge_entries = [
        {
            "category": "authentication",
            "intent": "password_reset",
            "keywords": ["password", "reset", "forgot", "login", "access", "can't log in"],
            "response_template": "I can help you reset your password right away. I'll send a password reset link to your registered email address. Please check your email (including spam folder) and follow the instructions to create a new password.",
            "follow_up_questions": [
                "What email address is associated with your account?",
                "Are you able to access your email?",
                "Have you checked your spam/junk folder?"
            ],
            "required_actions": ["send_password_reset_link", "verify_identity"],
            "can_auto_resolve": True,
            "requires_approval": False,
            "escalation_triggers": ["multiple_failed_attempts", "email_not_accessible"]
        },
        {
            "category": "authentication",
            "intent": "account_unlock",
            "keywords": ["locked", "unlock", "account", "disabled", "suspended", "blocked"],
            "response_template": "I see your account is locked. This usually happens after multiple failed login attempts. I can unlock your account immediately. Your account should be accessible within 2-3 minutes.",
            "follow_up_questions": [
                "Do you remember your current password?",
                "Have you been trying to log in recently?"
            ],
            "required_actions": ["unlock_account", "verify_identity"],
            "can_auto_resolve": True,
            "requires_approval": False,
            "escalation_triggers": ["security_concerns", "repeated_lockouts"]
        },
        {
            "category": "access",
            "intent": "access_request",
            "keywords": ["access", "permission", "need", "request", "system", "application", "folder"],
            "response_template": "I can help you request access to systems and applications. To process your request efficiently, I'll need to know which specific system or application you need access to, and what level of access you require.",
            "follow_up_questions": [
                "Which system or application do you need access to?",
                "What type of access do you need (read-only, full access, admin)?",
                "Is this for a specific project or ongoing work?",
                "Who is your manager or team lead?"
            ],
            "required_actions": ["create_access_request", "check_permissions"],
            "can_auto_resolve": False,
            "requires_approval": True,
            "escalation_triggers": ["admin_access_needed", "sensitive_system"]
        },
        {
            "category": "application",
            "intent": "software_install",
            "keywords": ["install", "software", "application", "program", "tool", "need"],
            "response_template": "I can help you with software installation requests. Let me check our approved software catalog and create an installation request for you. Most standard business applications can be installed within 24 hours.",
            "follow_up_questions": [
                "What software do you need installed?",
                "Is this for business use?",
                "Do you have a specific version requirement?",
                "Is this software already approved by your organization?"
            ],
            "required_actions": ["check_software_catalog", "create_install_request"],
            "can_auto_resolve": False,
            "requires_approval": True,
            "escalation_triggers": ["unapproved_software", "security_risk"]
        },
        {
            "category": "infrastructure",
            "intent": "hardware_issue",
            "keywords": ["computer", "laptop", "hardware", "broken", "not working", "screen", "keyboard", "mouse"],
            "response_template": "I'm sorry to hear you're having hardware problems. I'll create a support ticket and schedule a technician to assist you. For urgent issues, we can also arrange a temporary replacement device.",
            "follow_up_questions": [
                "What type of hardware issue are you experiencing?",
                "Is your device completely unusable or partially working?",
                "Do you need a temporary replacement device?",
                "What's your location/office?"
            ],
            "required_actions": ["create_hardware_ticket", "schedule_technician"],
            "can_auto_resolve": False,
            "requires_approval": False,
            "escalation_triggers": ["urgent_replacement_needed", "data_recovery_required"]
        },
        {
            "category": "network",
            "intent": "network_issue",
            "keywords": ["internet", "network", "wifi", "connection", "slow", "can't connect", "vpn"],
            "response_template": "I understand you're experiencing network connectivity issues. Let me run some diagnostics and check the network status for your location. I can also provide troubleshooting steps to resolve common connectivity problems.",
            "follow_up_questions": [
                "Are you connected to office WiFi or working remotely?",
                "Is the issue affecting all devices or just one?",
                "When did you first notice the problem?",
                "Are you able to access some websites but not others?"
            ],
            "required_actions": ["check_network_status", "run_diagnostics"],
            "can_auto_resolve": True,
            "requires_approval": False,
            "escalation_triggers": ["widespread_outage", "security_concerns"]
        },
        {
            "category": "application",
            "intent": "application_error",
            "keywords": ["error", "not working", "crashed", "frozen", "slow", "application", "software"],
            "response_template": "I can help you troubleshoot application errors. Let me check the application status and gather some details about the error you're experiencing. Many common application issues can be resolved quickly.",
            "follow_up_questions": [
                "Which application is having problems?",
                "What error message are you seeing?",
                "When did the problem start?",
                "Have you tried restarting the application?"
            ],
            "required_actions": ["check_application_status", "gather_error_details"],
            "can_auto_resolve": True,
            "requires_approval": False,
            "escalation_triggers": ["data_loss_risk", "business_critical_app"]
        },
        {
            "category": "general",
            "intent": "general_inquiry",
            "keywords": ["help", "question", "how", "what", "where", "when", "support"],
            "response_template": "I'm here to help you with any IT-related questions or issues. I can assist with password resets, account access, software requests, hardware problems, and much more. What specific issue can I help you with today?",
            "follow_up_questions": [
                "What type of issue are you experiencing?",
                "Is this related to hardware, software, or account access?",
                "How urgent is this issue for your work?"
            ],
            "required_actions": ["search_knowledge_base", "provide_general_help"],
            "can_auto_resolve": False,
            "requires_approval": False,
            "escalation_triggers": ["complex_technical_issue", "policy_question"]
        },
        {
            "category": "security",
            "intent": "security_concern",
            "keywords": ["security", "suspicious", "virus", "malware", "phishing", "hack", "breach"],
            "response_template": "Thank you for reporting a security concern. Security issues are taken very seriously. I'm immediately escalating this to our security team for investigation. Please do not click any suspicious links or provide personal information until this is resolved.",
            "follow_up_questions": [
                "What type of security issue are you reporting?",
                "Have you clicked any suspicious links or downloaded anything?",
                "Are you seeing any unusual behavior on your device?",
                "When did you first notice this issue?"
            ],
            "required_actions": ["escalate_to_security", "isolate_if_needed"],
            "can_auto_resolve": False,
            "requires_approval": True,
            "escalation_triggers": ["always_escalate"]
        },
        {
            "category": "email",
            "intent": "email_issue",
            "keywords": ["email", "outlook", "mail", "not receiving", "can't send", "sync"],
            "response_template": "I can help you resolve email issues. Email problems are often related to connectivity, account settings, or server issues. Let me check the email server status and guide you through some troubleshooting steps.",
            "follow_up_questions": [
                "Are you unable to send emails, receive emails, or both?",
                "What email client are you using (Outlook, web browser, mobile app)?",
                "Are you seeing any specific error messages?",
                "When did the email issue start?"
            ],
            "required_actions": ["check_email_server", "verify_account_settings"],
            "can_auto_resolve": True,
            "requires_approval": False,
            "escalation_triggers": ["server_outage", "account_compromise_suspected"]
        }
    ]
    
    for entry_data in knowledge_entries:
        knowledge = VirtualAgentKnowledge(
            organization_id=org_id,
            **entry_data
        )
        db.add(knowledge)
    
    await db.commit()
    print(f"✓ Created {len(knowledge_entries)} virtual agent knowledge entries")


async def main():
    """Main seeding function."""
    async with AsyncSessionLocal() as db:
        try:
            # Get the first organization
            from sqlalchemy import select
            
            result = await db.execute(select(Organization))
            org = result.scalars().first()
            
            if not org:
                print("❌ No organization found. Please run the main seed script first.")
                return
            
            print(f"Seeding virtual agent knowledge for organization: {org.name}")
            
            # Seed virtual agent knowledge
            await seed_virtual_agent_knowledge(db, str(org.id))
            
            print("\n✅ Virtual agent knowledge seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
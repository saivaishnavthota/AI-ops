import logging
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Ticket, User
from app.models.user import UserRole
from app.core.config import settings
from app.config.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class GitHubService:
    """Service to automatically fetch GitHub repository data and create tickets."""
    
    def __init__(self):
        self.github_repo = "saivaishnavthota/TicketingSystem"
        self.github_api_base = "https://api.github.com"
        self.github_token = getattr(settings, 'GITHUB_TOKEN', None)
        self.last_check_file = "last_github_check.txt"
        
    async def get_github_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Ops-Platform/1.0"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers
    
    async def get_last_check_time(self) -> datetime:
        """Get the last time we checked GitHub."""
        try:
            with open(self.last_check_file, 'r') as f:
                timestamp = f.read().strip()
                return datetime.fromisoformat(timestamp)
        except (FileNotFoundError, ValueError):
            # If no file or invalid format, check last 24 hours
            return datetime.now(timezone.utc) - timedelta(hours=24)
    
    async def save_last_check_time(self, timestamp: datetime):
        """Save the last check time."""
        try:
            with open(self.last_check_file, 'w') as f:
                f.write(timestamp.isoformat())
        except Exception as e:
            logger.error(f"Failed to save last check time: {e}")
    
    async def fetch_github_issues(self, since: datetime) -> List[Dict[str, Any]]:
        """Fetch issues from GitHub repository since the given time."""
        url = f"{self.github_api_base}/repos/{self.github_repo}/issues"
        params = {
            "state": "all",
            "since": since.isoformat(),
            "sort": "created",
            "direction": "desc",
            "per_page": 100
        }
        
        headers = await self.get_github_headers()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        issues = await response.json()
                        # Filter out pull requests (they appear as issues in GitHub API)
                        return [issue for issue in issues if 'pull_request' not in issue]
                    else:
                        logger.error(f"GitHub API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GitHub issues: {e}")
            return []
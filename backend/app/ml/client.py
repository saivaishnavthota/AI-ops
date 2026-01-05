"""
Anthropic Claude AI Client for AI-Ops Platform

Provides async interface to Anthropic Claude API for:
- Text generation
- Classification
- Structured JSON output
"""

import httpx
import json
import logging
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config.settings import settings

logger = logging.getLogger(__name__)


class AnthropicClient:
    """Async client for Anthropic Claude API."""

    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        # Check if this is an OAuth token (contains 'oat') or regular API key
        is_oauth_token = 'oat' in self.api_key.lower() if self.api_key else False

        if is_oauth_token:
            # Use Bearer token authentication for OAuth
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "anthropic-version": self.API_VERSION,
                "Content-Type": "application/json",
            }
        else:
            # Use x-api-key for standard API keys
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.API_VERSION,
                "Content-Type": "application/json",
            }

        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=120.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Send a message request to Anthropic Claude API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: System prompt for Claude
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            Dict containing the API response
        """
        # Convert messages format - Claude uses 'user' and 'assistant' roles
        claude_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            # Claude doesn't use 'system' in messages, it's a separate param
            if role == "system":
                continue
            # Map roles
            if role not in ["user", "assistant"]:
                role = "user"
            claude_messages.append({
                "role": role,
                "content": msg.get("content", "")
            })

        payload = {
            "model": model or self.model,
            "messages": claude_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = await self.client.post("/messages", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Anthropic API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Anthropic client error: {str(e)}")
            raise

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated text string
        """
        messages = [{"role": "user", "content": prompt}]

        response = await self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Extract content from Claude's response format
        content_blocks = response.get("content", [])
        if content_blocks and len(content_blocks) > 0:
            return content_blocks[0].get("text", "")
        return ""

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON from a prompt.

        Args:
            prompt: User prompt requesting JSON output
            system_prompt: Optional system prompt
            temperature: Sampling temperature (lower for more deterministic)
            max_tokens: Maximum tokens

        Returns:
            Parsed JSON dictionary
        """
        # Enhance prompt to request JSON output
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON. No other text before or after the JSON."

        # Enhance system prompt for JSON
        enhanced_system = system_prompt or ""
        if enhanced_system:
            enhanced_system += "\n\nYou must respond with valid JSON only. No markdown, no code blocks, just pure JSON."
        else:
            enhanced_system = "You must respond with valid JSON only. No markdown, no code blocks, just pure JSON."

        messages = [{"role": "user", "content": json_prompt}]

        response = await self.chat_completion(
            messages=messages,
            system_prompt=enhanced_system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Extract content from Claude's response format
        content_blocks = response.get("content", [])
        content = ""
        if content_blocks and len(content_blocks) > 0:
            content = content_blocks[0].get("text", "")

        # Clean up the response - remove any markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {content}")
            raise ValueError(f"Invalid JSON response from Claude: {e}")


# Singleton instance for reuse
_client_instance: Optional[AnthropicClient] = None


async def get_anthropic_client() -> AnthropicClient:
    """Get or create an Anthropic client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = AnthropicClient()
    return _client_instance


# Backwards compatibility alias
MistralClient = AnthropicClient
get_mistral_client = get_anthropic_client

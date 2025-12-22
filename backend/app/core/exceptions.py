from typing import Any, Dict, Optional


class AIOpsPlatformException(Exception):
    """Base exception for AI-Ops Platform."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AIOpsPlatformException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(AIOpsPlatformException):
    """Authorization failed - insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403)


class NotFoundError(AIOpsPlatformException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=message, status_code=404)


class ValidationError(AIOpsPlatformException):
    """Validation error."""

    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class ConflictError(AIOpsPlatformException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


class RateLimitError(AIOpsPlatformException):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=429)


class ServiceUnavailableError(AIOpsPlatformException):
    """Service temporarily unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message=message, status_code=503)

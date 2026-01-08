"""
External Ticketing System Integration Service
Integrates with the GitHub ticketing system to fetch auto-generated tickets
"""

import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID

from app.config.settings import settings
from app.models.ticket import Ticket, TicketStatus, TicketPriority

logger = logging.getLogger(__name__)


class ExternalTicketingService:
    """Service to integrate with external ticketing systems."""
    
    def __init__(self):
        # External API URL from settings
        self.external_api_url = settings.EXTERNAL_TICKETING_API_URL
        self.timeout = 30.0
        
    async def fetch_external_tickets(
        self, 
        limit: int = 50,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch tickets from the external ticketing system.
        
        Args:
            limit: Maximum number of tickets to fetch
            status_filter: Optional status filter
            
        Returns:
            List of external tickets formatted for our system
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First try to get incidents directly
                params = {
                    'pageSize': min(limit, 100),  # Limit to prevent overload
                    'page': 1
                }
                
                if status_filter:
                    # Map our status to external system status
                    external_status = self._map_status_to_external(status_filter)
                    if external_status:
                        params['status'] = external_status
                
                # Try incidents endpoint first
                try:
                    response = await client.get(
                        f"{self.external_api_url}/api/incidents",
                        params=params,
                        headers={
                            'Accept': 'application/json',
                            'User-Agent': 'AI-Ops-Platform/1.0'
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        incidents = data.get('data', []) if isinstance(data, dict) else data
                        return self._process_external_incidents(incidents, limit)
                        
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        logger.info("External API requires authentication, trying mock generator")
                    else:
                        logger.warning(f"External incidents API returned {e.response.status_code}")
                
                # Fallback to mock generator if incidents endpoint requires auth
                try:
                    mock_response = await client.get(
                        f"{self.external_api_url}/api/mock-generator/tickets",
                        params={'count': min(limit, 20)},  # Generate some mock tickets
                        headers={
                            'Accept': 'application/json',
                            'User-Agent': 'AI-Ops-Platform/1.0'
                        }
                    )
                    
                    if mock_response.status_code == 200:
                        mock_data = mock_response.json()
                        mock_tickets = mock_data.get('tickets', [])
                        
                        # Convert mock tickets to incident format
                        mock_incidents = []
                        for i, ticket in enumerate(mock_tickets):
                            mock_incident = {
                                'id': f"mock_{i+1}",
                                'number': f"INC-{1000 + i}",
                                'title': ticket.get('title', 'Mock Incident'),
                                'description': ticket.get('description', 'Auto-generated mock incident'),
                                'status': 'New',
                                'priority': ticket.get('priority', 'Medium'),
                                'category': ticket.get('category', 'General'),
                                'reporter': ticket.get('requesterName', 'External System'),
                                'createdAt': datetime.now(timezone.utc).isoformat(),
                                'updatedAt': datetime.now(timezone.utc).isoformat(),
                                'affectedCIs': [],
                                'history': []
                            }
                            mock_incidents.append(mock_incident)
                        
                        return self._process_external_incidents(mock_incidents, limit)
                        
                except Exception as mock_error:
                    logger.warning(f"Mock generator also failed: {mock_error}")
                
                logger.warning("Could not fetch external tickets from any endpoint")
                return []
                    
        except httpx.TimeoutException:
            logger.error("Timeout while fetching external tickets")
            return []
        except httpx.ConnectError:
            logger.warning("Could not connect to external ticketing system - it may be offline")
            return []
        except Exception as e:
            logger.error(f"Error fetching external tickets: {e}")
            return []
    
    def _process_external_incidents(self, incidents: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Process and convert external incidents to our ticket format."""
        external_tickets = []
        for incident in incidents[:limit]:
            try:
                ticket = self._convert_external_incident_to_ticket(incident)
                if ticket:
                    external_tickets.append(ticket)
            except Exception as e:
                logger.warning(f"Failed to convert external incident {incident.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(external_tickets)} external tickets")
        return external_tickets
    
    async def get_external_ticket_by_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific ticket from the external system by ID.
        
        Args:
            external_id: The external system's ticket ID
            
        Returns:
            External ticket data or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.external_api_url}/api/incidents/{external_id}",
                    headers={
                        'Accept': 'application/json',
                        'User-Agent': 'AI-Ops-Platform/1.0'
                    }
                )
                
                if response.status_code == 200:
                    incident = response.json()
                    return self._convert_external_incident_to_ticket(incident)
                elif response.status_code == 404:
                    return None
                else:
                    logger.warning(f"External API returned status {response.status_code} for ticket {external_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching external ticket {external_id}: {e}")
            return None
    
    async def get_external_system_status(self) -> Dict[str, Any]:
        """
        Check the status of the external ticketing system.
        
        Returns:
            Status information about the external system
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.external_api_url}/health",
                    headers={'Accept': 'application/json'}
                )
                
                if response.status_code == 200:
                    return {
                        'status': 'online',
                        'response_time_ms': response.elapsed.total_seconds() * 1000,
                        'api_url': self.external_api_url,
                        'last_checked': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        'status': 'error',
                        'error': f"HTTP {response.status_code}",
                        'api_url': self.external_api_url,
                        'last_checked': datetime.now(timezone.utc).isoformat()
                    }
                    
        except httpx.ConnectError:
            return {
                'status': 'offline',
                'error': 'Connection failed',
                'api_url': self.external_api_url,
                'last_checked': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'api_url': self.external_api_url,
                'last_checked': datetime.now(timezone.utc).isoformat()
            }
    
    def _convert_external_incident_to_ticket(self, incident: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert an external incident to our ticket format.
        
        Args:
            incident: External incident data
            
        Returns:
            Ticket data in our format
        """
        try:
            # Map external priority to our priority system
            external_priority = incident.get('priority', 'Medium')
            priority = self._map_priority_from_external(external_priority)
            
            # Map external status to our status system
            external_status = incident.get('status', 'New')
            status = self._map_status_from_external(external_status)
            
            # Extract dates
            created_at = self._parse_date(incident.get('createdAt'))
            updated_at = self._parse_date(incident.get('updatedAt'))
            resolved_at = self._parse_date(incident.get('resolvedAt')) if incident.get('resolvedAt') else None
            
            # Build ticket data
            ticket_data = {
                'id': f"ext_{incident.get('id', 'unknown')}",  # Prefix to identify external tickets
                'external_id': incident.get('id'),
                'external_number': incident.get('number', ''),
                'subject': incident.get('title', 'External Ticket'),
                'description': incident.get('description', ''),
                'status': status,
                'priority': priority,
                'category': incident.get('category', 'External'),
                'requester_name': incident.get('reporter', 'External System'),
                'assignee_name': incident.get('assignee'),
                'created_at': created_at,
                'updated_at': updated_at,
                'resolved_at': resolved_at,
                'source': 'external',
                'external_url': f"{self.external_api_url}/incidents/{incident.get('id')}",
                'comments': self._extract_comments(incident),
                'affected_cis': incident.get('affectedCIs', []),
                'sla_deadlines': incident.get('slaDeadlines'),
            }
            
            return ticket_data
            
        except Exception as e:
            logger.error(f"Error converting external incident: {e}")
            return None
    
    def _map_priority_from_external(self, external_priority: str) -> str:
        """Map external priority to our priority system."""
        priority_mapping = {
            'Critical': 'urgent',
            'High': 'high', 
            'Medium': 'normal',
            'Low': 'low'
        }
        return priority_mapping.get(external_priority, 'normal')
    
    def _map_priority_to_external(self, our_priority: str) -> str:
        """Map our priority to external priority system."""
        priority_mapping = {
            'urgent': 'Critical',
            'high': 'High',
            'normal': 'Medium', 
            'low': 'Low'
        }
        return priority_mapping.get(our_priority, 'Medium')
    
    def _map_status_from_external(self, external_status: str) -> str:
        """Map external status to our status system."""
        status_mapping = {
            'New': 'open',
            'InProgress': 'in_progress',
            'Pending': 'pending',
            'Resolved': 'resolved',
            'Closed': 'closed'
        }
        return status_mapping.get(external_status, 'open')
    
    def _map_status_to_external(self, our_status: str) -> str:
        """Map our status to external status system."""
        status_mapping = {
            'open': 'New',
            'in_progress': 'InProgress',
            'pending': 'Pending',
            'resolved': 'Resolved',
            'closed': 'Closed'
        }
        return status_mapping.get(our_status, 'New')
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
            
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                # Try parsing as timestamp
                return datetime.fromtimestamp(float(date_str), tz=timezone.utc)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse date: {date_str}")
                return None
    
    def _extract_comments(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and format comments from external incident."""
        comments = []
        
        # Extract history as comments
        history = incident.get('history', [])
        for entry in history:
            try:
                comment = {
                    'user': 'External System',
                    'text': f"Status changed from {entry.get('fromStatus', 'Unknown')} to {entry.get('toStatus', 'Unknown')}",
                    'time': self._parse_date(entry.get('timestamp')),
                    'external_transition': True
                }
                
                if entry.get('comment'):
                    comment['text'] += f" - {entry['comment']}"
                
                comments.append(comment)
            except Exception as e:
                logger.warning(f"Error extracting comment from history entry: {e}")
                continue
        
        return comments


# Global instance
external_ticketing_service = ExternalTicketingService()
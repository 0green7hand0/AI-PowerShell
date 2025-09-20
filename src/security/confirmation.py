"""User confirmation workflows for elevated privileges"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable
import uuid

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Permission, AuditEventType


class ConfirmationResult(Enum):
    """Result of user confirmation request"""
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ConfirmationRequest:
    """Request for user confirmation"""
    request_id: str
    command: str
    required_permissions: List[Permission]
    risk_description: str
    timestamp: datetime
    session_id: str
    timeout_seconds: int = 30
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class ConfirmationResponse:
    """Response to confirmation request"""
    request_id: str
    result: ConfirmationResult
    user_comment: Optional[str]
    timestamp: datetime
    response_time_seconds: float
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


class ConfirmationProviderInterface(ABC):
    """Abstract interface for confirmation providers"""
    
    @abstractmethod
    def request_confirmation(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """Request user confirmation for elevated privileges"""
        pass


class ConsoleConfirmationProvider(ConfirmationProviderInterface):
    """Console-based confirmation provider"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def request_confirmation(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """Request confirmation via console input"""
        start_time = datetime.utcnow()
        
        try:
            # Display confirmation prompt
            print("\n" + "="*60)
            print("SECURITY CONFIRMATION REQUIRED")
            print("="*60)
            print(f"Command: {request.command}")
            print(f"Required Permissions: {[p.value for p in request.required_permissions]}")
            print(f"Risk Description: {request.risk_description}")
            print(f"Session ID: {request.session_id}")
            print("-"*60)
            
            # Get user input with timeout simulation
            response = input("Do you want to proceed? (yes/no/comment): ").strip()
            response_lower = response.lower()
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            # Parse response
            if response_lower in ['yes', 'y', 'approve', 'approved']:
                result = ConfirmationResult.APPROVED
                comment = None
            elif response_lower in ['no', 'n', 'deny', 'denied']:
                result = ConfirmationResult.DENIED
                comment = None
            elif response_lower.startswith('comment:'):
                # Allow user to provide comment with denial
                result = ConfirmationResult.DENIED
                comment = response[8:].strip()  # Keep original case from original response
            else:
                result = ConfirmationResult.DENIED
                comment = f"Invalid response: {response}"
            
            return ConfirmationResponse(
                request_id=request.request_id,
                result=result,
                user_comment=comment,
                timestamp=end_time,
                response_time_seconds=response_time
            )
            
        except KeyboardInterrupt:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            return ConfirmationResponse(
                request_id=request.request_id,
                result=ConfirmationResult.DENIED,
                user_comment="User cancelled with Ctrl+C",
                timestamp=end_time,
                response_time_seconds=response_time
            )
        except Exception as e:
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Error during confirmation: {e}")
            return ConfirmationResponse(
                request_id=request.request_id,
                result=ConfirmationResult.ERROR,
                user_comment=f"Error: {str(e)}",
                timestamp=end_time,
                response_time_seconds=response_time
            )


class MockConfirmationProvider(ConfirmationProviderInterface):
    """Mock confirmation provider for testing"""
    
    def __init__(self, default_response: ConfirmationResult = ConfirmationResult.DENIED):
        self.default_response = default_response
        self.responses: Dict[str, ConfirmationResult] = {}
        self.requests: List[ConfirmationRequest] = []
        self.logger = logging.getLogger(__name__)
    
    def set_response(self, request_id: str, response: ConfirmationResult):
        """Set specific response for a request ID"""
        self.responses[request_id] = response
    
    def set_default_response(self, response: ConfirmationResult):
        """Set default response for all requests"""
        self.default_response = response
    
    def request_confirmation(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """Mock confirmation request"""
        self.requests.append(request)
        
        # Get response (specific or default)
        result = self.responses.get(request.request_id, self.default_response)
        
        return ConfirmationResponse(
            request_id=request.request_id,
            result=result,
            user_comment=f"Mock response: {result.value}",
            timestamp=datetime.utcnow(),
            response_time_seconds=0.1
        )


class ConfirmationManager:
    """Manages user confirmation workflows and audit trails"""
    
    def __init__(self, provider: ConfirmationProviderInterface, audit_logger: Optional[Callable] = None):
        """Initialize confirmation manager"""
        self.provider = provider
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Track confirmation history
        self.confirmation_history: List[tuple[ConfirmationRequest, ConfirmationResponse]] = []
    
    def request_permission_confirmation(
        self, 
        command: str, 
        required_permissions: List[Permission],
        session_id: str,
        risk_description: str = "",
        timeout_seconds: int = 30
    ) -> ConfirmationResponse:
        """Request user confirmation for elevated permissions"""
        
        # Create confirmation request
        request = ConfirmationRequest(
            request_id=str(uuid.uuid4()),
            command=command,
            required_permissions=required_permissions,
            risk_description=risk_description or self._generate_risk_description(required_permissions),
            timestamp=datetime.utcnow(),
            session_id=session_id,
            timeout_seconds=timeout_seconds
        )
        
        self.logger.info(f"Requesting confirmation for command: {command[:100]}...")
        
        # Log confirmation request
        if self.audit_logger:
            self.audit_logger(
                event_type=AuditEventType.SECURITY_VALIDATION,
                session_id=session_id,
                data={
                    "confirmation_request": {
                        "request_id": request.request_id,
                        "command": command,
                        "required_permissions": [p.value for p in required_permissions],
                        "risk_description": risk_description
                    }
                }
            )
        
        # Get user response
        response = self.provider.request_confirmation(request)
        
        # Store in history
        self.confirmation_history.append((request, response))
        
        # Log confirmation response
        if self.audit_logger:
            self.audit_logger(
                event_type=AuditEventType.SECURITY_VALIDATION,
                session_id=session_id,
                data={
                    "confirmation_response": {
                        "request_id": response.request_id,
                        "result": response.result.value,
                        "user_comment": response.user_comment,
                        "response_time_seconds": response.response_time_seconds
                    }
                }
            )
        
        self.logger.info(f"Confirmation result: {response.result.value} (took {response.response_time_seconds:.2f}s)")
        
        return response
    
    def get_confirmation_history(self, session_id: Optional[str] = None) -> List[tuple[ConfirmationRequest, ConfirmationResponse]]:
        """Get confirmation history, optionally filtered by session"""
        if session_id:
            return [(req, resp) for req, resp in self.confirmation_history if req.session_id == session_id]
        return self.confirmation_history.copy()
    
    def get_confirmation_stats(self, session_id: Optional[str] = None) -> Dict[str, int]:
        """Get confirmation statistics"""
        history = self.get_confirmation_history(session_id)
        
        stats = {
            "total_requests": len(history),
            "approved": 0,
            "denied": 0,
            "timeout": 0,
            "error": 0
        }
        
        for _, response in history:
            if response.result == ConfirmationResult.APPROVED:
                stats["approved"] += 1
            elif response.result == ConfirmationResult.DENIED:
                stats["denied"] += 1
            elif response.result == ConfirmationResult.TIMEOUT:
                stats["timeout"] += 1
            elif response.result == ConfirmationResult.ERROR:
                stats["error"] += 1
        
        return stats
    
    def _generate_risk_description(self, permissions: List[Permission]) -> str:
        """Generate risk description based on required permissions"""
        if Permission.ADMIN in permissions:
            return "This command requires administrative privileges and may modify system settings or access sensitive resources."
        elif Permission.WRITE in permissions:
            return "This command will modify files or system state."
        elif Permission.EXECUTE in permissions:
            return "This command will execute external programs or scripts."
        else:
            return "This command requires elevated permissions."


class PermissionEscalationLogger:
    """Specialized logger for permission escalation events"""
    
    def __init__(self, audit_logger: Optional[Callable] = None):
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        self.escalation_events: List[Dict] = []
    
    def log_escalation_attempt(
        self, 
        session_id: str, 
        command: str, 
        required_permissions: List[Permission],
        confirmation_result: ConfirmationResult,
        user_comment: Optional[str] = None
    ):
        """Log permission escalation attempt"""
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "command": command,
            "required_permissions": [p.value for p in required_permissions],
            "confirmation_result": confirmation_result.value,
            "user_comment": user_comment,
            "event_type": "permission_escalation"
        }
        
        self.escalation_events.append(event)
        
        # Log to standard logger
        self.logger.warning(
            f"Permission escalation attempt: {confirmation_result.value} - "
            f"Command: {command[:100]}... - "
            f"Permissions: {[p.value for p in required_permissions]} - "
            f"Session: {session_id}"
        )
        
        # Log to audit system if available
        if self.audit_logger:
            self.audit_logger(
                event_type=AuditEventType.SECURITY_VALIDATION,
                session_id=session_id,
                data=event
            )
    
    def get_escalation_events(self, session_id: Optional[str] = None) -> List[Dict]:
        """Get escalation events, optionally filtered by session"""
        if session_id:
            return [event for event in self.escalation_events if event["session_id"] == session_id]
        return self.escalation_events.copy()
    
    def get_escalation_summary(self, session_id: Optional[str] = None) -> Dict[str, int]:
        """Get summary of escalation events"""
        events = self.get_escalation_events(session_id)
        
        summary = {
            "total_attempts": len(events),
            "approved": len([e for e in events if e["confirmation_result"] == "approved"]),
            "denied": len([e for e in events if e["confirmation_result"] == "denied"]),
            "timeout": len([e for e in events if e["confirmation_result"] == "timeout"]),
            "error": len([e for e in events if e["confirmation_result"] == "error"])
        }
        
        return summary
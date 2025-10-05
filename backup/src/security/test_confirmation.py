"""Unit tests for user confirmation workflows"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Permission, AuditEventType
from security.confirmation import (
    ConfirmationRequest, ConfirmationResponse, ConfirmationResult,
    ConsoleConfirmationProvider, MockConfirmationProvider,
    ConfirmationManager, PermissionEscalationLogger
)


class TestConfirmationRequest(unittest.TestCase):
    """Test cases for ConfirmationRequest"""
    
    def test_initialization_with_defaults(self):
        """Test ConfirmationRequest initialization with default values"""
        request = ConfirmationRequest(
            request_id="",
            command="Get-Process",
            required_permissions=[Permission.READ],
            risk_description="Test risk",
            timestamp=None,
            session_id="test-session"
        )
        
        # Should generate ID and timestamp
        self.assertIsNotNone(request.request_id)
        self.assertNotEqual(request.request_id, "")
        self.assertIsInstance(request.timestamp, datetime)
        self.assertEqual(request.timeout_seconds, 30)  # Default value
    
    def test_initialization_with_values(self):
        """Test ConfirmationRequest initialization with provided values"""
        timestamp = datetime.utcnow()
        request = ConfirmationRequest(
            request_id="test-123",
            command="Stop-Service Spooler",
            required_permissions=[Permission.ADMIN],
            risk_description="Administrative action required",
            timestamp=timestamp,
            session_id="session-456",
            timeout_seconds=60
        )
        
        self.assertEqual(request.request_id, "test-123")
        self.assertEqual(request.command, "Stop-Service Spooler")
        self.assertEqual(request.required_permissions, [Permission.ADMIN])
        self.assertEqual(request.risk_description, "Administrative action required")
        self.assertEqual(request.timestamp, timestamp)
        self.assertEqual(request.session_id, "session-456")
        self.assertEqual(request.timeout_seconds, 60)


class TestConfirmationResponse(unittest.TestCase):
    """Test cases for ConfirmationResponse"""
    
    def test_initialization_with_defaults(self):
        """Test ConfirmationResponse initialization with default values"""
        response = ConfirmationResponse(
            request_id="test-123",
            result=ConfirmationResult.APPROVED,
            user_comment=None,
            timestamp=None,
            response_time_seconds=1.5
        )
        
        # Should generate timestamp
        self.assertIsInstance(response.timestamp, datetime)
    
    def test_initialization_with_values(self):
        """Test ConfirmationResponse initialization with provided values"""
        timestamp = datetime.utcnow()
        response = ConfirmationResponse(
            request_id="test-123",
            result=ConfirmationResult.DENIED,
            user_comment="Too risky",
            timestamp=timestamp,
            response_time_seconds=2.3
        )
        
        self.assertEqual(response.request_id, "test-123")
        self.assertEqual(response.result, ConfirmationResult.DENIED)
        self.assertEqual(response.user_comment, "Too risky")
        self.assertEqual(response.timestamp, timestamp)
        self.assertEqual(response.response_time_seconds, 2.3)


class TestMockConfirmationProvider(unittest.TestCase):
    """Test cases for MockConfirmationProvider"""
    
    def setUp(self):
        """Set up test environment"""
        self.provider = MockConfirmationProvider()
    
    def test_default_response(self):
        """Test default response behavior"""
        request = ConfirmationRequest(
            request_id="test-123",
            command="Get-Process",
            required_permissions=[Permission.READ],
            risk_description="Test",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        response = self.provider.request_confirmation(request)
        
        self.assertEqual(response.request_id, "test-123")
        self.assertEqual(response.result, ConfirmationResult.DENIED)  # Default
        self.assertIn("Mock response", response.user_comment)
    
    def test_specific_response(self):
        """Test setting specific response for request ID"""
        self.provider.set_response("test-123", ConfirmationResult.APPROVED)
        
        request = ConfirmationRequest(
            request_id="test-123",
            command="Stop-Service Spooler",
            required_permissions=[Permission.ADMIN],
            risk_description="Admin required",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        response = self.provider.request_confirmation(request)
        
        self.assertEqual(response.result, ConfirmationResult.APPROVED)
    
    def test_change_default_response(self):
        """Test changing default response"""
        self.provider.set_default_response(ConfirmationResult.APPROVED)
        
        request = ConfirmationRequest(
            request_id="test-456",
            command="Get-Service",
            required_permissions=[],
            risk_description="Safe command",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        response = self.provider.request_confirmation(request)
        
        self.assertEqual(response.result, ConfirmationResult.APPROVED)
    
    def test_request_tracking(self):
        """Test that requests are tracked"""
        request1 = ConfirmationRequest(
            request_id="test-1",
            command="Command 1",
            required_permissions=[Permission.READ],
            risk_description="Test 1",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        request2 = ConfirmationRequest(
            request_id="test-2",
            command="Command 2",
            required_permissions=[Permission.WRITE],
            risk_description="Test 2",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        self.provider.request_confirmation(request1)
        self.provider.request_confirmation(request2)
        
        self.assertEqual(len(self.provider.requests), 2)
        self.assertEqual(self.provider.requests[0].request_id, "test-1")
        self.assertEqual(self.provider.requests[1].request_id, "test-2")


class TestConsoleConfirmationProvider(unittest.TestCase):
    """Test cases for ConsoleConfirmationProvider"""
    
    def setUp(self):
        """Set up test environment"""
        self.provider = ConsoleConfirmationProvider()
    
    @patch('builtins.input')
    def test_approval_responses(self, mock_input):
        """Test various approval responses"""
        approval_inputs = ['yes', 'y', 'approve', 'approved', 'YES', 'Y']
        
        for input_value in approval_inputs:
            with self.subTest(input_value=input_value):
                mock_input.return_value = input_value
                
                request = ConfirmationRequest(
                    request_id="test-123",
                    command="Get-Process",
                    required_permissions=[Permission.READ],
                    risk_description="Test",
                    timestamp=datetime.utcnow(),
                    session_id="session-1"
                )
                
                response = self.provider.request_confirmation(request)
                
                self.assertEqual(response.result, ConfirmationResult.APPROVED)
                self.assertIsNone(response.user_comment)
    
    @patch('builtins.input')
    def test_denial_responses(self, mock_input):
        """Test various denial responses"""
        denial_inputs = ['no', 'n', 'deny', 'denied', 'NO', 'N', 'invalid']
        
        for input_value in denial_inputs:
            with self.subTest(input_value=input_value):
                mock_input.return_value = input_value
                
                request = ConfirmationRequest(
                    request_id="test-123",
                    command="Remove-Item C:\\temp -Force",
                    required_permissions=[Permission.WRITE],
                    risk_description="Destructive operation",
                    timestamp=datetime.utcnow(),
                    session_id="session-1"
                )
                
                response = self.provider.request_confirmation(request)
                
                self.assertEqual(response.result, ConfirmationResult.DENIED)
    
    @patch('builtins.input')
    def test_comment_response(self, mock_input):
        """Test comment response"""
        mock_input.return_value = "comment: This is too risky for production"
        
        request = ConfirmationRequest(
            request_id="test-123",
            command="Format-Volume C:",
            required_permissions=[Permission.ADMIN],
            risk_description="Critical system operation",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        response = self.provider.request_confirmation(request)
        
        self.assertEqual(response.result, ConfirmationResult.DENIED)
        self.assertEqual(response.user_comment, "This is too risky for production")
    
    @patch('builtins.input')
    def test_keyboard_interrupt(self, mock_input):
        """Test handling of keyboard interrupt (Ctrl+C)"""
        mock_input.side_effect = KeyboardInterrupt()
        
        request = ConfirmationRequest(
            request_id="test-123",
            command="Stop-Computer",
            required_permissions=[Permission.ADMIN],
            risk_description="System shutdown",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        response = self.provider.request_confirmation(request)
        
        self.assertEqual(response.result, ConfirmationResult.DENIED)
        self.assertIn("Ctrl+C", response.user_comment)
    
    @patch('builtins.input')
    def test_exception_handling(self, mock_input):
        """Test handling of unexpected exceptions"""
        mock_input.side_effect = Exception("Test error")
        
        request = ConfirmationRequest(
            request_id="test-123",
            command="Get-Service",
            required_permissions=[Permission.READ],
            risk_description="Safe operation",
            timestamp=datetime.utcnow(),
            session_id="session-1"
        )
        
        response = self.provider.request_confirmation(request)
        
        self.assertEqual(response.result, ConfirmationResult.ERROR)
        self.assertIn("Error", response.user_comment)


class TestConfirmationManager(unittest.TestCase):
    """Test cases for ConfirmationManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_provider = MockConfirmationProvider()
        self.mock_audit_logger = MagicMock()
        self.manager = ConfirmationManager(self.mock_provider, self.mock_audit_logger)
    
    def test_request_permission_confirmation(self):
        """Test requesting permission confirmation"""
        self.mock_provider.set_default_response(ConfirmationResult.APPROVED)
        
        response = self.manager.request_permission_confirmation(
            command="Stop-Service Spooler",
            required_permissions=[Permission.ADMIN],
            session_id="session-123",
            risk_description="Service management operation"
        )
        
        self.assertEqual(response.result, ConfirmationResult.APPROVED)
        self.assertEqual(len(self.manager.confirmation_history), 1)
        
        # Check audit logging
        self.assertEqual(self.mock_audit_logger.call_count, 2)  # Request and response
    
    def test_confirmation_history_tracking(self):
        """Test confirmation history tracking"""
        # Make multiple requests
        for i in range(3):
            self.manager.request_permission_confirmation(
                command=f"Command {i}",
                required_permissions=[Permission.WRITE],
                session_id="session-123"
            )
        
        history = self.manager.get_confirmation_history()
        self.assertEqual(len(history), 3)
        
        # Test session filtering
        session_history = self.manager.get_confirmation_history("session-123")
        self.assertEqual(len(session_history), 3)
        
        other_session_history = self.manager.get_confirmation_history("other-session")
        self.assertEqual(len(other_session_history), 0)
    
    def test_confirmation_statistics(self):
        """Test confirmation statistics"""
        # Set up different responses
        responses = [
            ConfirmationResult.APPROVED,
            ConfirmationResult.DENIED,
            ConfirmationResult.APPROVED,
            ConfirmationResult.TIMEOUT
        ]
        
        for i, result in enumerate(responses):
            self.mock_provider.set_response(f"req-{i}", result)
            
            request = ConfirmationRequest(
                request_id=f"req-{i}",
                command=f"Command {i}",
                required_permissions=[Permission.ADMIN],
                risk_description="Test",
                timestamp=datetime.utcnow(),
                session_id="session-123"
            )
            
            self.mock_provider.request_confirmation(request)
            self.manager.confirmation_history.append((request, ConfirmationResponse(
                request_id=f"req-{i}",
                result=result,
                user_comment=None,
                timestamp=datetime.utcnow(),
                response_time_seconds=1.0
            )))
        
        stats = self.manager.get_confirmation_stats()
        
        self.assertEqual(stats["total_requests"], 4)
        self.assertEqual(stats["approved"], 2)
        self.assertEqual(stats["denied"], 1)
        self.assertEqual(stats["timeout"], 1)
        self.assertEqual(stats["error"], 0)
    
    def test_risk_description_generation(self):
        """Test automatic risk description generation"""
        test_cases = [
            ([Permission.ADMIN], "administrative privileges"),
            ([Permission.WRITE], "modify files"),
            ([Permission.EXECUTE], "execute external programs"),
            ([Permission.READ], "elevated permissions")  # Default case
        ]
        
        for permissions, expected_text in test_cases:
            with self.subTest(permissions=permissions):
                description = self.manager._generate_risk_description(permissions)
                self.assertIn(expected_text, description.lower())


class TestPermissionEscalationLogger(unittest.TestCase):
    """Test cases for PermissionEscalationLogger"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_audit_logger = MagicMock()
        self.escalation_logger = PermissionEscalationLogger(self.mock_audit_logger)
    
    def test_log_escalation_attempt(self):
        """Test logging escalation attempts"""
        self.escalation_logger.log_escalation_attempt(
            session_id="session-123",
            command="Set-ExecutionPolicy RemoteSigned",
            required_permissions=[Permission.ADMIN],
            confirmation_result=ConfirmationResult.APPROVED,
            user_comment="Needed for script execution"
        )
        
        # Check event was stored
        events = self.escalation_logger.get_escalation_events()
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event["session_id"], "session-123")
        self.assertEqual(event["command"], "Set-ExecutionPolicy RemoteSigned")
        self.assertEqual(event["required_permissions"], ["admin"])
        self.assertEqual(event["confirmation_result"], "approved")
        self.assertEqual(event["user_comment"], "Needed for script execution")
        
        # Check audit logger was called
        self.mock_audit_logger.assert_called_once()
    
    def test_escalation_events_filtering(self):
        """Test filtering escalation events by session"""
        # Log events for different sessions
        sessions = ["session-1", "session-2", "session-1"]
        
        for i, session in enumerate(sessions):
            self.escalation_logger.log_escalation_attempt(
                session_id=session,
                command=f"Command {i}",
                required_permissions=[Permission.ADMIN],
                confirmation_result=ConfirmationResult.APPROVED
            )
        
        # Test filtering
        all_events = self.escalation_logger.get_escalation_events()
        self.assertEqual(len(all_events), 3)
        
        session1_events = self.escalation_logger.get_escalation_events("session-1")
        self.assertEqual(len(session1_events), 2)
        
        session2_events = self.escalation_logger.get_escalation_events("session-2")
        self.assertEqual(len(session2_events), 1)
    
    def test_escalation_summary(self):
        """Test escalation summary statistics"""
        # Log various escalation attempts
        attempts = [
            ConfirmationResult.APPROVED,
            ConfirmationResult.DENIED,
            ConfirmationResult.APPROVED,
            ConfirmationResult.TIMEOUT,
            ConfirmationResult.ERROR
        ]
        
        for i, result in enumerate(attempts):
            self.escalation_logger.log_escalation_attempt(
                session_id="session-123",
                command=f"Command {i}",
                required_permissions=[Permission.ADMIN],
                confirmation_result=result
            )
        
        summary = self.escalation_logger.get_escalation_summary()
        
        self.assertEqual(summary["total_attempts"], 5)
        self.assertEqual(summary["approved"], 2)
        self.assertEqual(summary["denied"], 1)
        self.assertEqual(summary["timeout"], 1)
        self.assertEqual(summary["error"], 1)


class TestConfirmationIntegration(unittest.TestCase):
    """Integration tests for confirmation system"""
    
    def test_end_to_end_confirmation_workflow(self):
        """Test complete confirmation workflow"""
        # Set up components
        provider = MockConfirmationProvider(ConfirmationResult.APPROVED)
        audit_logger = MagicMock()
        manager = ConfirmationManager(provider, audit_logger)
        escalation_logger = PermissionEscalationLogger(audit_logger)
        
        # Simulate permission escalation workflow
        command = "Stop-Service -Name Spooler -Force"
        required_permissions = [Permission.ADMIN]
        session_id = "integration-test-session"
        
        # Request confirmation
        response = manager.request_permission_confirmation(
            command=command,
            required_permissions=required_permissions,
            session_id=session_id,
            risk_description="Service management requires admin privileges"
        )
        
        # Log escalation attempt
        escalation_logger.log_escalation_attempt(
            session_id=session_id,
            command=command,
            required_permissions=required_permissions,
            confirmation_result=response.result,
            user_comment=response.user_comment
        )
        
        # Verify workflow
        self.assertEqual(response.result, ConfirmationResult.APPROVED)
        
        # Check history
        history = manager.get_confirmation_history(session_id)
        self.assertEqual(len(history), 1)
        
        # Check escalation log
        escalation_events = escalation_logger.get_escalation_events(session_id)
        self.assertEqual(len(escalation_events), 1)
        
        # Check audit logging
        self.assertGreater(audit_logger.call_count, 0)


if __name__ == '__main__':
    unittest.main()
"""Unit tests for Docker sandbox execution environment"""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import ExecutionResult, Platform
from security.engine import SandboxManager


class TestSandboxManager(unittest.TestCase):
    """Test cases for SandboxManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.sandbox_config = {
            'image': 'mcr.microsoft.com/powershell:latest',
            'memory_limit': '256m',
            'cpu_limit': '0.5',
            'timeout': 30
        }
    
    @patch('security.engine.subprocess.run')
    def test_docker_availability_check_success(self, mock_run):
        """Test successful Docker availability check"""
        # Mock successful Docker version check
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
        ]
        
        # Should not raise exception
        manager = SandboxManager(**self.sandbox_config)
        self.assertIsNotNone(manager)
    
    @patch('security.engine.subprocess.run')
    def test_docker_availability_check_failure(self, mock_run):
        """Test Docker availability check failure"""
        # Mock Docker not available
        mock_run.side_effect = subprocess.CalledProcessError(1, 'docker')
        
        # Should raise RuntimeError
        with self.assertRaises(RuntimeError) as context:
            SandboxManager(**self.sandbox_config)
        
        self.assertIn("Docker sandbox unavailable", str(context.exception))
    
    @patch('security.engine.subprocess.run')
    def test_docker_image_pull_when_missing(self, mock_run):
        """Test Docker image pull when image is missing"""
        # Mock Docker version success, image inspect failure, pull success
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=1),  # docker image inspect (image not found)
            MagicMock(returncode=0),  # docker pull
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        
        # Verify pull was called
        expected_calls = [
            call(['docker', 'version'], capture_output=True, text=True, timeout=10),
            call(['docker', 'image', 'inspect', self.sandbox_config['image']], 
                 capture_output=True, text=True, timeout=10),
            call(['docker', 'pull', self.sandbox_config['image']], 
                 capture_output=True, text=True, timeout=300)
        ]
        mock_run.assert_has_calls(expected_calls)
    
    @patch('security.engine.subprocess.run')
    @patch('security.engine.tempfile.NamedTemporaryFile')
    @patch('security.engine.Path.unlink')
    def test_execute_command_success(self, mock_unlink, mock_tempfile, mock_run):
        """Test successful command execution in sandbox"""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = '/tmp/test_script.ps1'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock Docker availability check
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            # Command execution
            MagicMock(
                returncode=0,
                stdout="Process output",
                stderr="",
            )
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        result = manager.execute("Get-Process", 30)
        
        # Verify result
        self.assertIsInstance(result, ExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout, "Process output")
        self.assertEqual(result.stderr, "")
        self.assertTrue(result.sandbox_used)
        self.assertEqual(result.platform, Platform.LINUX)
        
        # Verify Docker command was called correctly
        docker_call = mock_run.call_args_list[-1]
        docker_cmd = docker_call[0][0]
        
        self.assertIn('docker', docker_cmd)
        self.assertIn('run', docker_cmd)
        self.assertIn('--rm', docker_cmd)
        self.assertIn('--memory', docker_cmd)
        self.assertIn('256m', docker_cmd)
        self.assertIn('--cpus', docker_cmd)
        self.assertIn('0.5', docker_cmd)
        self.assertIn('--network', docker_cmd)
        self.assertIn('none', docker_cmd)
        self.assertIn('--read-only', docker_cmd)
    
    @patch('security.engine.subprocess.run')
    @patch('security.engine.tempfile.NamedTemporaryFile')
    @patch('security.engine.Path.unlink')
    def test_execute_command_failure(self, mock_unlink, mock_tempfile, mock_run):
        """Test command execution failure in sandbox"""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = '/tmp/test_script.ps1'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock Docker availability check and failed execution
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            # Command execution failure
            MagicMock(
                returncode=1,
                stdout="",
                stderr="Command failed",
            )
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        result = manager.execute("Invalid-Command", 30)
        
        # Verify result
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 1)
        self.assertEqual(result.stderr, "Command failed")
        self.assertTrue(result.sandbox_used)
    
    @patch('security.engine.subprocess.run')
    @patch('security.engine.tempfile.NamedTemporaryFile')
    @patch('security.engine.Path.unlink')
    def test_execute_command_timeout(self, mock_unlink, mock_tempfile, mock_run):
        """Test command execution timeout in sandbox"""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = '/tmp/test_script.ps1'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock Docker availability check and timeout
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            # Command execution timeout
            subprocess.TimeoutExpired(['docker'], 30)
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        result = manager.execute("Start-Sleep 60", 30)
        
        # Verify result
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, -1)
        self.assertIn("timed out", result.stderr)
        self.assertTrue(result.sandbox_used)
        self.assertEqual(result.execution_time, 30)  # Should match timeout
    
    @patch('security.engine.subprocess.run')
    @patch('security.engine.tempfile.NamedTemporaryFile')
    @patch('security.engine.Path.unlink')
    def test_execute_command_exception(self, mock_unlink, mock_tempfile, mock_run):
        """Test command execution with unexpected exception"""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = '/tmp/test_script.ps1'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock Docker availability check and exception
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            # Command execution exception
            Exception("Docker daemon error")
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        result = manager.execute("Get-Process", 30)
        
        # Verify result
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, -1)
        self.assertIn("Sandbox execution failed", result.stderr)
        self.assertTrue(result.sandbox_used)
    
    @patch('security.engine.subprocess.run')
    def test_sandbox_security_features(self, mock_run):
        """Test that sandbox includes proper security features"""
        # Mock Docker availability check
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            MagicMock(returncode=0, stdout="", stderr="")  # execution
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        
        # Execute a command to trigger Docker run
        with patch('security.engine.tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = '/tmp/test_script.ps1'
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            with patch('security.engine.Path.unlink'):
                manager.execute("Get-Process", 30)
            
            # Check the Docker command for security features
            docker_call = mock_run.call_args_list[-1]
            docker_cmd = docker_call[0][0]
            
            # Verify security features
            self.assertIn('--network', docker_cmd)
            self.assertIn('none', docker_cmd)  # Network isolation
            self.assertIn('--read-only', docker_cmd)  # Read-only filesystem
            self.assertIn('--tmpfs', docker_cmd)  # Writable tmp directory
            self.assertIn('/tmp', docker_cmd)
            self.assertIn('--memory', docker_cmd)  # Memory limits
            self.assertIn('--cpus', docker_cmd)  # CPU limits
    
    @patch('security.engine.subprocess.run')
    def test_resource_limits_configuration(self, mock_run):
        """Test that resource limits are properly configured"""
        # Mock Docker availability check and execution
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            MagicMock(returncode=0, stdout="", stderr="")  # execution
        ]
        
        # Test with custom resource limits
        custom_config = {
            'image': 'test-image',
            'memory_limit': '512m',
            'cpu_limit': '1.0',
            'timeout': 60
        }
        
        manager = SandboxManager(**custom_config)
        
        # Execute a command to trigger Docker run
        with patch('security.engine.tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = '/tmp/test_script.ps1'
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            with patch('security.engine.Path.unlink'):
                manager.execute("Get-Process", 60)
            
            # Check the Docker command for resource limits
            docker_call = mock_run.call_args_list[-1]
            docker_cmd = docker_call[0][0]
            
            # Verify custom resource limits
            memory_index = docker_cmd.index('--memory')
            self.assertEqual(docker_cmd[memory_index + 1], '512m')
            
            cpu_index = docker_cmd.index('--cpus')
            self.assertEqual(docker_cmd[cpu_index + 1], '1.0')
    
    @patch('security.engine.subprocess.run')
    @patch('security.engine.tempfile.NamedTemporaryFile')
    def test_script_file_handling(self, mock_tempfile, mock_run):
        """Test proper handling of temporary script files"""
        # Setup mocks
        mock_file = MagicMock()
        mock_file.name = '/tmp/test_script.ps1'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock Docker availability check and execution
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            MagicMock(returncode=0, stdout="output", stderr="")  # execution
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        
        with patch('security.engine.Path.unlink') as mock_unlink:
            result = manager.execute("Get-Process | Select-Object Name", 30)
            
            # Verify script file was created and cleaned up
            mock_tempfile.assert_called_once()
            mock_file.write.assert_called_once_with("Get-Process | Select-Object Name")
            mock_unlink.assert_called_once()
    
    @patch('security.engine.subprocess.run')
    def test_volume_mounting_security(self, mock_run):
        """Test that volume mounting is secure"""
        # Mock Docker availability check and execution
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            MagicMock(returncode=0, stdout="", stderr="")  # execution
        ]
        
        manager = SandboxManager(**self.sandbox_config)
        
        # Execute a command to trigger Docker run
        with patch('security.engine.tempfile.NamedTemporaryFile') as mock_tempfile:
            mock_file = MagicMock()
            mock_file.name = '/tmp/test_script.ps1'
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            with patch('security.engine.Path.unlink'):
                manager.execute("Get-Process", 30)
            
            # Check the Docker command for volume mounting
            docker_call = mock_run.call_args_list[-1]
            docker_cmd = docker_call[0][0]
            
            # Verify volume is mounted read-only
            volume_index = docker_cmd.index('-v')
            volume_spec = docker_cmd[volume_index + 1]
            self.assertIn(':ro', volume_spec)  # Read-only mount


class TestSandboxManagerIntegration(unittest.TestCase):
    """Integration tests for SandboxManager"""
    
    @patch('security.engine.subprocess.run')
    def test_end_to_end_sandbox_workflow(self, mock_run):
        """Test complete sandbox workflow from initialization to execution"""
        # Mock all subprocess calls
        mock_run.side_effect = [
            # Docker availability checks
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
            # Command executions
            MagicMock(returncode=0, stdout="Process1\nProcess2", stderr=""),
            MagicMock(returncode=1, stdout="", stderr="Access denied"),
            MagicMock(returncode=0, stdout="Service stopped", stderr=""),
        ]
        
        # Initialize sandbox
        manager = SandboxManager(
            image='mcr.microsoft.com/powershell:latest',
            memory_limit='256m',
            cpu_limit='0.5',
            timeout=30
        )
        
        # Execute multiple commands
        commands = [
            "Get-Process | Select-Object Name",
            "Remove-Item C:\\Windows\\System32 -Recurse",  # Should fail
            "Stop-Service Spooler"
        ]
        
        results = []
        for command in commands:
            with patch('security.engine.tempfile.NamedTemporaryFile') as mock_tempfile:
                mock_file = MagicMock()
                mock_file.name = f'/tmp/script_{len(results)}.ps1'
                mock_tempfile.return_value.__enter__.return_value = mock_file
                
                with patch('security.engine.Path.unlink'):
                    result = manager.execute(command, 30)
                    results.append(result)
        
        # Verify results
        self.assertEqual(len(results), 3)
        
        # First command should succeed
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].stdout, "Process1\nProcess2")
        
        # Second command should fail (simulated security failure)
        self.assertFalse(results[1].success)
        self.assertEqual(results[1].stderr, "Access denied")
        
        # Third command should succeed
        self.assertTrue(results[2].success)
        self.assertEqual(results[2].stdout, "Service stopped")
        
        # All should be sandboxed
        for result in results:
            self.assertTrue(result.sandbox_used)
            self.assertEqual(result.platform, Platform.LINUX)
    
    @patch('security.engine.subprocess.run')
    def test_concurrent_sandbox_execution(self, mock_run):
        """Test concurrent command execution in sandbox"""
        import threading
        import time
        
        # Mock Docker availability check
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
        ]
        
        manager = SandboxManager(**{
            'image': 'mcr.microsoft.com/powershell:latest',
            'memory_limit': '128m',
            'cpu_limit': '0.25',
            'timeout': 10
        })
        
        results = []
        errors = []
        
        def execute_command(command_id):
            try:
                # Add execution mock for each thread
                with patch('security.engine.subprocess.run') as thread_mock_run:
                    thread_mock_run.return_value = MagicMock(
                        returncode=0,
                        stdout=f"Output from command {command_id}",
                        stderr=""
                    )
                    
                    with patch('security.engine.tempfile.NamedTemporaryFile') as mock_tempfile:
                        mock_file = MagicMock()
                        mock_file.name = f'/tmp/script_{command_id}.ps1'
                        mock_tempfile.return_value.__enter__.return_value = mock_file
                        
                        with patch('security.engine.Path.unlink'):
                            result = manager.execute(f"Get-Process # Command {command_id}", 10)
                            results.append((command_id, result))
            except Exception as e:
                errors.append((command_id, e))
        
        # Create and start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=execute_command, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=15)
        
        # Verify results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 5)
        
        # Verify all executions were successful
        for command_id, result in results:
            self.assertTrue(result.success, f"Command {command_id} failed")
            self.assertTrue(result.sandbox_used)
            self.assertIn(f"command {command_id}", result.stdout.lower())
    
    @patch('security.engine.subprocess.run')
    def test_sandbox_isolation_verification(self, mock_run):
        """Test that sandbox properly isolates commands"""
        # Mock Docker availability check
        mock_run.side_effect = [
            MagicMock(returncode=0),  # docker version
            MagicMock(returncode=0),  # docker image inspect
        ]
        
        manager = SandboxManager(**{
            'image': 'mcr.microsoft.com/powershell:latest',
            'memory_limit': '256m',
            'cpu_limit': '0.5',
            'timeout': 30
        })
        
        # Test commands that should be isolated
        isolation_tests = [
            ("Get-Process", "Should list container processes only"),
            ("Get-ChildItem C:\\", "Should see container filesystem only"),
            ("Test-NetConnection google.com", "Should fail due to network isolation"),
        ]
        
        for command, description in isolation_tests:
            with self.subTest(command=command, description=description):
                with patch('security.engine.tempfile.NamedTemporaryFile') as mock_tempfile:
                    mock_file = MagicMock()
                    mock_file.name = '/tmp/test_script.ps1'
                    mock_tempfile.return_value.__enter__.return_value = mock_file
                    
                    # Mock appropriate response for each test
                    with patch('security.engine.subprocess.run') as exec_mock:
                        if "Test-NetConnection" in command:
                            # Network should be blocked
                            exec_mock.return_value = MagicMock(
                                returncode=1,
                                stdout="",
                                stderr="Network unreachable"
                            )
                        else:
                            # Other commands should work but in isolated environment
                            exec_mock.return_value = MagicMock(
                                returncode=0,
                                stdout="Isolated output",
                                stderr=""
                            )
                    
                        with patch('security.engine.Path.unlink'):
                            result = manager.execute(command, 30)
                    
                        # Verify isolation
                        self.assertTrue(result.sandbox_used)
                        self.assertEqual(result.platform, Platform.LINUX)
                        
                        if "Test-NetConnection" in command:
                            # Network isolation should cause failure
                            self.assertFalse(result.success)
                            self.assertIn("unreachable", result.stderr.lower())


if __name__ == '__main__':
    unittest.main()
# Security Checker Guide

## Overview

The Security Checker is a comprehensive security validation system for PowerShell script templates. It detects dangerous commands, network access, and path traversal attacks to ensure templates are safe to use.

## Quick Start

### Basic Usage

```python
from src.template_engine.security_checker import SecurityChecker

# Create a security checker
checker = SecurityChecker()

# Check a script
script = """
param([string]$Path)
Remove-Item $Path -Recurse -Force
"""

result = checker.check_template(script)

if not result.is_safe:
    print("Security issues found:")
    for issue in result.issues:
        print(f"  [{issue.severity}] {issue.message}")
        print(f"    Line {issue.line_number}: {issue.code_snippet}")
```

### Integration with TemplateValidator

```python
from src.template_engine.template_validator import TemplateValidator

# Security checks are enabled by default
validator = TemplateValidator(enable_security_checks=True)

# Validate a template (includes security checks)
result = validator.validate_template(template)

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

## Security Levels

### Critical (Blocks template)
- Recursive force delete: `Remove-Item -Recurse -Force`
- Disk operations: `Format-Volume`, `Clear-Disk`
- System shutdown: `Stop-Computer`, `Restart-Computer`
- Partition operations: `Remove-Partition`, `Set-Partition`

### High (Blocks template)
- Force delete: `Remove-Item -Force`
- System directory access: `C:\Windows`, `C:\Program Files`
- Code execution: `Invoke-Expression`, `iex`
- Remote commands: `Invoke-Command`
- Service management: `New-Service`, `Set-Service`
- Unrestricted execution policy: `Set-ExecutionPolicy Unrestricted`

### Medium (Warning only)
- General delete: `Remove-Item`
- Recycle bin: `Clear-RecycleBin -Force`
- Network adapter: `Disable-NetAdapter`
- Firewall: `Set-NetFirewallProfile`

## Network Access Detection

### High Severity
- Web requests: `Invoke-WebRequest`, `Invoke-RestMethod`
- File transfer: `Start-BitsTransfer`
- Email: `Send-MailMessage`

### Medium Severity
- Network tests: `Test-Connection`, `Test-NetConnection`
- DNS: `Resolve-DnsName`

## Path Security

### Detected Patterns
- Path traversal: `../`, `..\`, URL-encoded variants
- Sensitive paths:
  - `C:\Windows\System32`
  - `C:\Program Files`
  - Registry: `HKLM:`, `HKCU:`

### Safe Paths
- User directories: `C:\Users\Documents`
- Project directories: `D:\Projects`
- Relative paths: `.\output`

## API Reference

### SecurityChecker

#### Methods

##### `check_template(script_content: str) -> SecurityCheckResult`
Performs complete security check on a script.

**Parameters:**
- `script_content`: PowerShell script content

**Returns:**
- `SecurityCheckResult` with `is_safe` flag and list of issues

##### `check_dangerous_commands(script_content: str) -> List[SecurityIssue]`
Checks for dangerous PowerShell commands.

##### `check_network_access(script_content: str) -> List[SecurityIssue]`
Checks for network access commands.

##### `validate_file_path(file_path: str) -> Tuple[bool, str]`
Validates a file path for security issues.

**Returns:**
- `(is_safe, error_message)` tuple

### SecurityIssue

```python
@dataclass
class SecurityIssue:
    severity: str       # 'critical', 'high', 'medium', 'low'
    category: str       # 'dangerous_command', 'path_traversal', 'network_access'
    message: str        # Description of the issue
    line_number: int    # Line where issue was found (0 if unknown)
    code_snippet: str   # Code that triggered the issue
```

### SecurityCheckResult

```python
@dataclass
class SecurityCheckResult:
    is_safe: bool              # True if no critical/high issues
    issues: List[SecurityIssue]  # All detected issues
```

## Configuration

### Enabling/Disabling Security Checks

```python
# Enable security checks (default)
validator = TemplateValidator(enable_security_checks=True)

# Disable security checks (not recommended)
validator = TemplateValidator(enable_security_checks=False)
```

### Custom Security Rules

Currently, security rules are defined in the `SecurityChecker` class. To customize:

1. Modify `DANGEROUS_COMMANDS` dictionary
2. Modify `NETWORK_COMMANDS` dictionary
3. Modify `PATH_TRAVERSAL_PATTERNS` list
4. Modify `SENSITIVE_PATHS` list

## Best Practices

### For Template Creators

1. **Avoid dangerous operations**: Use safe alternatives
   - ❌ `Remove-Item -Recurse -Force`
   - ✅ `Remove-Item -Confirm`

2. **Validate user input**: Always validate paths and parameters
   ```powershell
   if (Test-Path $UserPath) {
       # Safe operation
   }
   ```

3. **Use relative paths**: Avoid absolute system paths
   - ❌ `C:\Windows\System32\file.txt`
   - ✅ `.\output\file.txt`

4. **Limit network access**: Only when necessary
   - Document why network access is needed
   - Use HTTPS for security

### For Developers

1. **Always enable security checks** in production
2. **Handle security errors gracefully**
3. **Provide clear error messages** to users
4. **Log security issues** for audit purposes

## Examples

### Example 1: Safe Backup Script

```powershell
param(
    [string]$SourcePath,
    [string]$DestinationPath
)

if (Test-Path $SourcePath) {
    Copy-Item -Path $SourcePath -Destination $DestinationPath -Recurse
    Write-Host "Backup completed"
}
```

**Result:** ✅ Safe - No security issues

### Example 2: Unsafe Cleanup Script

```powershell
param([string]$TempPath)

# Dangerous: recursive force delete
Remove-Item $TempPath -Recurse -Force
```

**Result:** ❌ Unsafe - Critical: dangerous command detected

### Example 3: Network Download Script

```powershell
param(
    [string]$Url,
    [string]$OutputPath
)

Invoke-WebRequest -Uri $Url -OutFile $OutputPath
```

**Result:** ❌ Unsafe - High: network access detected

## Troubleshooting

### False Positives

If a command is flagged incorrectly:

1. Check if it's in a comment (should be skipped)
2. Verify the command pattern
3. Consider if the operation is truly safe

### False Negatives

If a dangerous command is not detected:

1. Check the command pattern in `DANGEROUS_COMMANDS`
2. Add the pattern if missing
3. Submit a bug report

### Disabling Checks for Specific Templates

If you need to bypass security checks for a specific use case:

```python
# Create validator without security checks
validator = TemplateValidator(enable_security_checks=False)

# Or check security separately
checker = SecurityChecker()
result = checker.check_template(script)
# Review issues manually and decide
```

## Testing

### Running Security Tests

```bash
# Run all security tests
python -m pytest tests/template_engine/test_security_checker.py -v

# Run integration tests
python -m pytest tests/template_engine/test_validator_security_integration.py -v

# Run all tests
python -m pytest tests/template_engine/test_security*.py -v
```

### Writing Security Tests

```python
def test_custom_dangerous_command():
    checker = SecurityChecker()
    script = "Your-Dangerous-Command"
    
    result = checker.check_template(script)
    
    assert not result.is_safe
    assert len(result.issues) > 0
    assert result.issues[0].severity == 'critical'
```

## Future Enhancements

1. **Configurable rules**: Allow users to customize security rules
2. **Whitelist mechanism**: Allow specific commands in certain contexts
3. **Security reports**: Generate detailed security audit reports
4. **Auto-fix suggestions**: Provide safe alternatives for detected issues
5. **Sandbox testing**: Test templates in isolated environment

## Support

For issues or questions:
1. Check the test files for examples
2. Review the source code documentation
3. Submit an issue on GitHub

## License

This security checker is part of the MCP PowerShell project and follows the same license.

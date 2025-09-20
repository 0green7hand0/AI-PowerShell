#!/bin/bash
# AI PowerShell Assistant Health Check Script
# Comprehensive health monitoring and verification

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_URL="http://localhost:8000"
TIMEOUT=30
VERBOSE=false
OUTPUT_FORMAT="text"
ALERT_WEBHOOK=""
LOG_FILE=""

# Health check results
HEALTH_STATUS="UNKNOWN"
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0
HEALTH_DETAILS=()

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    [ -n "$LOG_FILE" ] && echo "[$(date)] INFO: $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    [ -n "$LOG_FILE" ] && echo "[$(date)] SUCCESS: $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    [ -n "$LOG_FILE" ] && echo "[$(date)] WARNING: $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    [ -n "$LOG_FILE" ] && echo "[$(date)] ERROR: $1" >> "$LOG_FILE"
}

show_help() {
    cat << EOF
AI PowerShell Assistant Health Check Script

Usage: $0 [OPTIONS]

Options:
  -u, --url URL           Server URL (default: http://localhost:8000)
  -t, --timeout SECONDS   Request timeout (default: 30)
  -v, --verbose          Enable verbose output
  -f, --format FORMAT    Output format (text|json|prometheus)
  -w, --webhook URL      Alert webhook URL
  -l, --log-file FILE    Log file path
  -h, --help             Show this help message

Examples:
  $0                                    # Basic health check
  $0 -u http://server:8000 -v          # Check remote server with verbose output
  $0 -f json                           # JSON output format
  $0 -w http://alerts.example.com      # Send alerts to webhook

Exit Codes:
  0 - All checks passed (HEALTHY)
  1 - Some checks failed (DEGRADED)
  2 - Critical checks failed (UNHEALTHY)
  3 - Server unreachable (DOWN)

EOF
}

# Health check functions
check_server_connectivity() {
    local check_name="Server Connectivity"
    log_info "Checking $check_name..."
    
    if curl -f -s --max-time "$TIMEOUT" "$SERVER_URL/health" >/dev/null 2>&1; then
        log_success "$check_name: OK"
        HEALTH_DETAILS+=("$check_name:OK")
        ((CHECKS_PASSED++))
        return 0
    else
        log_error "$check_name: FAILED - Server unreachable"
        HEALTH_DETAILS+=("$check_name:FAILED")
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_health_endpoint() {
    local check_name="Health Endpoint"
    log_info "Checking $check_name..."
    
    local response=$(curl -s --max-time "$TIMEOUT" "$SERVER_URL/health" 2>/dev/null)
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$SERVER_URL/health" 2>/dev/null)
    
    if [ "$status_code" = "200" ]; then
        if echo "$response" | grep -q '"status".*"healthy"'; then
            log_success "$check_name: OK"
            HEALTH_DETAILS+=("$check_name:OK")
            ((CHECKS_PASSED++))
            return 0
        else
            log_warning "$check_name: WARNING - Unhealthy status reported"
            HEALTH_DETAILS+=("$check_name:WARNING")
            ((CHECKS_WARNING++))
            return 1
        fi
    else
        log_error "$check_name: FAILED - HTTP $status_code"
        HEALTH_DETAILS+=("$check_name:FAILED")
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_api_functionality() {
    local check_name="API Functionality"
    log_info "Checking $check_name..."
    
    # Test natural language processing endpoint
    local test_payload='{"input_text": "get current date"}'
    local response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$SERVER_URL/natural_language_to_powershell" \
        -H "Content-Type: application/json" \
        -d "$test_payload" 2>/dev/null)
    
    if echo "$response" | grep -q '"success".*true'; then
        log_success "$check_name: OK"
        HEALTH_DETAILS+=("$check_name:OK")
        ((CHECKS_PASSED++))
        return 0
    else
        log_error "$check_name: FAILED - API not responding correctly"
        HEALTH_DETAILS+=("$check_name:FAILED")
        ((CHECKS_FAILED++))
        [ "$VERBOSE" = true ] && log_info "Response: $response"
        return 1
    fi
}

check_ai_engine() {
    local check_name="AI Engine"
    log_info "Checking $check_name..."
    
    # Test AI processing with a simple request
    local test_payload='{"input_text": "list processes", "session_id": "health_check"}'
    local response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$SERVER_URL/natural_language_to_powershell" \
        -H "Content-Type: application/json" \
        -d "$test_payload" 2>/dev/null)
    
    if echo "$response" | grep -q '"generated_command"'; then
        local confidence=$(echo "$response" | grep -o '"confidence_score":[0-9.]*' | cut -d: -f2)
        if [ -n "$confidence" ] && (( $(echo "$confidence > 0.5" | bc -l) )); then
            log_success "$check_name: OK (confidence: $confidence)"
            HEALTH_DETAILS+=("$check_name:OK")
            ((CHECKS_PASSED++))
            return 0
        else
            log_warning "$check_name: WARNING - Low confidence score: $confidence"
            HEALTH_DETAILS+=("$check_name:WARNING")
            ((CHECKS_WARNING++))
            return 1
        fi
    else
        log_error "$check_name: FAILED - AI processing not working"
        HEALTH_DETAILS+=("$check_name:FAILED")
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_powershell_execution() {
    local check_name="PowerShell Execution"
    log_info "Checking $check_name..."
    
    # Test PowerShell command execution
    local test_payload='{"command": "Get-Date", "session_id": "health_check", "use_sandbox": false}'
    local response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$SERVER_URL/execute_powershell_command" \
        -H "Content-Type: application/json" \
        -d "$test_payload" 2>/dev/null)
    
    if echo "$response" | grep -q '"success".*true'; then
        log_success "$check_name: OK"
        HEALTH_DETAILS+=("$check_name:OK")
        ((CHECKS_PASSED++))
        return 0
    else
        log_error "$check_name: FAILED - PowerShell execution not working"
        HEALTH_DETAILS+=("$check_name:FAILED")
        ((CHECKS_FAILED++))
        [ "$VERBOSE" = true ] && log_info "Response: $response"
        return 1
    fi
}

check_security_validation() {
    local check_name="Security Validation"
    log_info "Checking $check_name..."
    
    # Test security validation with a dangerous command
    local test_payload='{"command": "Remove-Item C:\\ -Recurse -Force", "session_id": "health_check"}'
    local response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$SERVER_URL/execute_powershell_command" \
        -H "Content-Type: application/json" \
        -d "$test_payload" 2>/dev/null)
    
    # This should be blocked by security
    if echo "$response" | grep -q '"success".*false'; then
        log_success "$check_name: OK - Dangerous command blocked"
        HEALTH_DETAILS+=("$check_name:OK")
        ((CHECKS_PASSED++))
        return 0
    else
        log_error "$check_name: FAILED - Security validation not working"
        HEALTH_DETAILS+=("$check_name:FAILED")
        ((CHECKS_FAILED++))
        return 1
    fi
}

check_system_info() {
    local check_name="System Information"
    log_info "Checking $check_name..."
    
    # Test system information endpoint
    local test_payload='{"session_id": "health_check", "include_modules": false}'
    local response=$(curl -s --max-time "$TIMEOUT" \
        -X POST "$SERVER_URL/get_powershell_info" \
        -H "Content-Type: application/json" \
        -d "$test_payload" 2>/dev/null)
    
    if echo "$response" | grep -q '"success".*true'; then
        log_success "$check_name: OK"
        HEALTH_DETAILS+=("$check_name:OK")
        ((CHECKS_PASSED++))
        return 0
    else
        log_warning "$check_name: WARNING - System info not available"
        HEALTH_DETAILS+=("$check_name:WARNING")
        ((CHECKS_WARNING++))
        return 1
    fi
}

check_performance_metrics() {
    local check_name="Performance Metrics"
    log_info "Checking $check_name..."
    
    # Check if metrics endpoint is available
    local response=$(curl -s --max-time "$TIMEOUT" "$SERVER_URL/metrics" 2>/dev/null)
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$SERVER_URL/metrics" 2>/dev/null)
    
    if [ "$status_code" = "200" ]; then
        log_success "$check_name: OK"
        HEALTH_DETAILS+=("$check_name:OK")
        ((CHECKS_PASSED++))
        return 0
    else
        log_warning "$check_name: WARNING - Metrics endpoint not available"
        HEALTH_DETAILS+=("$check_name:WARNING")
        ((CHECKS_WARNING++))
        return 1
    fi
}

check_resource_usage() {
    local check_name="Resource Usage"
    log_info "Checking $check_name..."
    
    # Get system resource usage (if available)
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}' 2>/dev/null || echo "unknown")
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}' 2>/dev/null || echo "unknown")
    
    if [ "$cpu_usage" != "unknown" ] && [ "$memory_usage" != "unknown" ]; then
        # Check if resource usage is within acceptable limits
        if (( $(echo "$cpu_usage < 80" | bc -l 2>/dev/null || echo 1) )) && \
           (( $(echo "$memory_usage < 90" | bc -l 2>/dev/null || echo 1) )); then
            log_success "$check_name: OK (CPU: ${cpu_usage}%, Memory: ${memory_usage}%)"
            HEALTH_DETAILS+=("$check_name:OK")
            ((CHECKS_PASSED++))
            return 0
        else
            log_warning "$check_name: WARNING - High resource usage (CPU: ${cpu_usage}%, Memory: ${memory_usage}%)"
            HEALTH_DETAILS+=("$check_name:WARNING")
            ((CHECKS_WARNING++))
            return 1
        fi
    else
        log_warning "$check_name: WARNING - Unable to determine resource usage"
        HEALTH_DETAILS+=("$check_name:WARNING")
        ((CHECKS_WARNING++))
        return 1
    fi
}

determine_overall_health() {
    local total_checks=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))
    
    if [ "$CHECKS_FAILED" -eq 0 ] && [ "$CHECKS_WARNING" -eq 0 ]; then
        HEALTH_STATUS="HEALTHY"
        return 0
    elif [ "$CHECKS_FAILED" -eq 0 ] && [ "$CHECKS_WARNING" -gt 0 ]; then
        HEALTH_STATUS="DEGRADED"
        return 1
    elif [ "$CHECKS_FAILED" -gt 0 ] && [ "$CHECKS_PASSED" -gt 0 ]; then
        HEALTH_STATUS="UNHEALTHY"
        return 2
    else
        HEALTH_STATUS="DOWN"
        return 3
    fi
}

output_results() {
    local format="$1"
    local exit_code="$2"
    
    case "$format" in
        "json")
            cat << EOF
{
  "status": "$HEALTH_STATUS",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "checks": {
    "passed": $CHECKS_PASSED,
    "failed": $CHECKS_FAILED,
    "warning": $CHECKS_WARNING,
    "total": $((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))
  },
  "details": [
$(IFS=$'\n'; for detail in "${HEALTH_DETAILS[@]}"; do
    name=$(echo "$detail" | cut -d: -f1)
    status=$(echo "$detail" | cut -d: -f2)
    echo "    {\"check\": \"$name\", \"status\": \"$status\"}"
done | sed '$!s/$/,/')
  ],
  "exit_code": $exit_code
}
EOF
            ;;
        "prometheus")
            echo "# HELP powershell_assistant_health Health status of AI PowerShell Assistant"
            echo "# TYPE powershell_assistant_health gauge"
            case "$HEALTH_STATUS" in
                "HEALTHY") echo "powershell_assistant_health 1" ;;
                "DEGRADED") echo "powershell_assistant_health 0.5" ;;
                "UNHEALTHY") echo "powershell_assistant_health 0.25" ;;
                "DOWN") echo "powershell_assistant_health 0" ;;
            esac
            
            echo "# HELP powershell_assistant_checks_total Total number of health checks"
            echo "# TYPE powershell_assistant_checks_total counter"
            echo "powershell_assistant_checks_total{status=\"passed\"} $CHECKS_PASSED"
            echo "powershell_assistant_checks_total{status=\"failed\"} $CHECKS_FAILED"
            echo "powershell_assistant_checks_total{status=\"warning\"} $CHECKS_WARNING"
            ;;
        *)
            echo "Health Check Results"
            echo "==================="
            echo "Overall Status: $HEALTH_STATUS"
            echo "Timestamp: $(date)"
            echo ""
            echo "Summary:"
            echo "  Passed: $CHECKS_PASSED"
            echo "  Failed: $CHECKS_FAILED"
            echo "  Warning: $CHECKS_WARNING"
            echo "  Total: $((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))"
            echo ""
            echo "Details:"
            for detail in "${HEALTH_DETAILS[@]}"; do
                name=$(echo "$detail" | cut -d: -f1)
                status=$(echo "$detail" | cut -d: -f2)
                case "$status" in
                    "OK") echo -e "  ${GREEN}✓${NC} $name" ;;
                    "WARNING") echo -e "  ${YELLOW}⚠${NC} $name" ;;
                    "FAILED") echo -e "  ${RED}✗${NC} $name" ;;
                esac
            done
            ;;
    esac
}

send_alert() {
    local webhook_url="$1"
    local status="$2"
    local exit_code="$3"
    
    if [ -n "$webhook_url" ] && [ "$status" != "HEALTHY" ]; then
        log_info "Sending alert to webhook..."
        
        local alert_payload=$(cat << EOF
{
  "alert": "AI PowerShell Assistant Health Check",
  "status": "$status",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "server_url": "$SERVER_URL",
  "checks_failed": $CHECKS_FAILED,
  "checks_warning": $CHECKS_WARNING,
  "exit_code": $exit_code
}
EOF
)
        
        if curl -s --max-time 10 \
            -X POST "$webhook_url" \
            -H "Content-Type: application/json" \
            -d "$alert_payload" >/dev/null 2>&1; then
            log_success "Alert sent successfully"
        else
            log_warning "Failed to send alert to webhook"
        fi
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            SERVER_URL="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -w|--webhook)
            ALERT_WEBHOOK="$2"
            shift 2
            ;;
        -l|--log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main health check process
main() {
    [ "$OUTPUT_FORMAT" = "text" ] && echo "AI PowerShell Assistant Health Check"
    [ "$OUTPUT_FORMAT" = "text" ] && echo "==================================="
    [ "$OUTPUT_FORMAT" = "text" ] && echo "Server: $SERVER_URL"
    [ "$OUTPUT_FORMAT" = "text" ] && echo "Timeout: ${TIMEOUT}s"
    [ "$OUTPUT_FORMAT" = "text" ] && echo ""
    
    # Run health checks
    check_server_connectivity || true
    check_health_endpoint || true
    check_api_functionality || true
    check_ai_engine || true
    check_powershell_execution || true
    check_security_validation || true
    check_system_info || true
    check_performance_metrics || true
    check_resource_usage || true
    
    # Determine overall health status
    determine_overall_health
    local exit_code=$?
    
    # Output results
    output_results "$OUTPUT_FORMAT" "$exit_code"
    
    # Send alert if configured
    send_alert "$ALERT_WEBHOOK" "$HEALTH_STATUS" "$exit_code"
    
    return $exit_code
}

# Run main function
main "$@"
# Test online installation scripts
Write-Host "Testing AI PowerShell Assistant online installation scripts" -ForegroundColor Blue
Write-Host "==========================================================="

# Test script accessibility
Write-Host "Testing script accessibility..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.ps1" -Method Head
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: PowerShell install script is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: PowerShell install script access failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Linux script
Write-Host "Testing Linux install script..." -ForegroundColor Yellow
try {
    $linuxResponse = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.sh" -Method Head
    if ($linuxResponse.StatusCode -eq 200) {
        Write-Host "SUCCESS: Linux install script is accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "ERROR: Linux install script access failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Online installation scripts test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Users can install using:"
Write-Host "Windows: Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.ps1' -OutFile 'install.ps1'; .\install.ps1"
Write-Host "Linux/macOS: curl -fsSL https://raw.githubusercontent.com/0green7hand0/AI-PowerShell/main/scripts/install.sh | bash"
# GitHub Release Creation Script
param(
    [string]$Token = $env:GITHUB_TOKEN,
    [string]$Owner = "0green7hand0",
    [string]$Repo = "AI-PowerShell",
    [string]$Tag = "v1.1.0"
)

if (-not $Token) {
    Write-Host "Error: GITHUB_TOKEN environment variable is required" -ForegroundColor Red
    exit 1
}

$releaseNotesFile = "v1.1.0-Release描述.md"
if (-not (Test-Path $releaseNotesFile)) {
    Write-Host "Error: $releaseNotesFile not found" -ForegroundColor Red
    exit 1
}

$releaseNotes = Get-Content $releaseNotesFile -Raw -Encoding UTF8

$releaseData = @{
    tag_name = $Tag
    target_commitish = "main"
    name = "AI PowerShell v1.1.0 - Dual Version Release"
    body = $releaseNotes
    draft = $false
    prerelease = $false
} | ConvertTo-Json -Depth 10

$apiUrl = "https://api.github.com/repos/$Owner/$Repo/releases"

$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "PowerShell-Script"
}

Write-Host "Creating GitHub Release..." -ForegroundColor Green
Write-Host "Repository: $Owner/$Repo" -ForegroundColor Cyan
Write-Host "Tag: $Tag" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $releaseData -ContentType "application/json"
    
    Write-Host "GitHub Release created successfully!" -ForegroundColor Green
    Write-Host "Release URL: $($response.html_url)" -ForegroundColor Yellow
    Write-Host "Download links:" -ForegroundColor Cyan
    Write-Host "  ZIP: $($response.zipball_url)" -ForegroundColor White
    Write-Host "  TAR: $($response.tarball_url)" -ForegroundColor White
    
    Start-Process $response.html_url
    
} catch {
    Write-Host "Failed to create Release:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
# ekko installer for Windows
# Run with: powershell -ExecutionPolicy Bypass -File install-ekko.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 ekko installer for Windows" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: Python 3 is required but not installed" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Install requests if needed
Write-Host "Checking dependencies..." -ForegroundColor Blue
python -c "import requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Installing requests module..." -ForegroundColor Yellow
    python -m pip install requests --quiet --user
}
Write-Host "✓ Dependencies ready" -ForegroundColor Green

# Create directories
$installDir = "$env:LOCALAPPDATA\ekko"
$configDir = "$env:APPDATA\ekko"
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

# Copy or download ekko
if (Test-Path "ekko.py") {
    Write-Host "ℹ Installing from local file..." -ForegroundColor Blue
    Copy-Item "ekko.py" "$installDir\ekko.py"
} else {
    Write-Host "ℹ Downloading ekko..." -ForegroundColor Blue
    $url = "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/ekko/main/ekko.py"
    Invoke-WebRequest -Uri $url -OutFile "$installDir\ekko.py"
}

# Create wrapper batch file
$batchContent = @"
@echo off
python "$installDir\ekko.py" %*
"@
$batchContent | Out-File -FilePath "$installDir\ekko.bat" -Encoding ASCII

Write-Host "✓ ekko installed to $installDir" -ForegroundColor Green

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installDir*") {
    Write-Host "ℹ Adding to PATH..." -ForegroundColor Blue
    [Environment]::SetEnvironmentVariable(
        "Path",
        "$currentPath;$installDir",
        "User"
    )
    $env:Path = "$env:Path;$installDir"
}

Write-Host "✓ Shell integration complete" -ForegroundColor Green

# Run setup wizard
Write-Host "`n🔧 Running configuration wizard...`n" -ForegroundColor Cyan
& "$installDir\ekko.bat" --setup

# Final instructions
Write-Host "`n✅ Installation complete!`n" -ForegroundColor Green
Write-Host "Reload PowerShell or run:"
Write-Host "  `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User')" -ForegroundColor Blue
Write-Host "`nThen try:"
Write-Host "  ekko find all files over 500MB" -ForegroundColor Blue
Write-Host "`nReconfigure anytime with:"
Write-Host "  ekko --setup" -ForegroundColor Blue

# ════════════════════════════════════════════════════════════════════════════
# OSE PLATFORM - PowerShell Deployment Script for Windows
# ════════════════════════════════════════════════════════════════════════════

param(
    [string]$ServerHost = "167.235.58.24",
    [string]$ServerUser = "admin",
    [string]$ServerPath = "/var/www/ose-platform"
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Message)
    Write-ColorOutput "`n════════════════════════════════════════════════════════════════" "Green"
    Write-ColorOutput "   $Message" "Green"
    Write-ColorOutput "════════════════════════════════════════════════════════════════`n" "Green"
}

function Write-Step {
    param(
        [string]$Step,
        [string]$Message
    )
    Write-ColorOutput "[$Step] $Message" "Yellow"
}

Write-Header "OSE PLATFORM - Production Deployment"

# Check if plink (PuTTY) is available
$plinkPath = Get-Command plink -ErrorAction SilentlyContinue
if (-not $plinkPath) {
    Write-ColorOutput "ERROR: plink (PuTTY) not found. Please install PuTTY or use manual deployment." "Red"
    Write-ColorOutput "`nAlternative: Use WinSCP or follow manual instructions in DEPLOYMENT_INSTRUCTIONS.md" "Yellow"
    exit 1
}

# Server connection details
$serverConnection = "$ServerUser@$ServerHost"
$password = "bb474edf"

Write-Step "1/6" "Testing SSH connection..."
try {
    echo "y" | plink -ssh $serverConnection -pw $password "echo 'Connection successful'"
} catch {
    Write-ColorOutput "ERROR: Cannot connect to server. Check credentials and network." "Red"
    exit 1
}

Write-Step "2/6" "Creating deployment directory on server..."
echo "y" | plink -ssh $serverConnection -pw $password "mkdir -p $ServerPath && chown $ServerUser`:$ServerUser $ServerPath"

Write-Step "3/6" "Preparing files for upload..."
$projectRoot = $PSScriptRoot
$excludeDirs = @(
    "node_modules",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "dist",
    "build",
    "logs",
    "tmp",
    "backend-new-backup-*",
    "frontend-backup-*",
    "backend",
    "frontend",
    "frontend-invoice-portal",
    "frontend-picking-portal",
    "frontend-public-portal",
    ".claude"
)

Write-ColorOutput "`nIMPORTANT: File upload must be done manually using one of these methods:" "Yellow"
Write-ColorOutput "`n1. Using WinSCP (Recommended for Windows):" "Cyan"
Write-ColorOutput "   - Download: https://winscp.net/" "White"
Write-ColorOutput "   - Host: $ServerHost" "White"
Write-ColorOutput "   - User: $ServerUser" "White"
Write-ColorOutput "   - Password: $password" "White"
Write-ColorOutput "   - Upload to: $ServerPath" "White"

Write-ColorOutput "`n2. Using pscp (PuTTY SCP):" "Cyan"
Write-ColorOutput "   pscp -r -pw $password $projectRoot\* $serverConnection`:$ServerPath/" "White"

Write-ColorOutput "`n3. Using Git Bash with rsync:" "Cyan"
Write-ColorOutput "   rsync -avz --progress --exclude='node_modules' ./ $serverConnection`:$ServerPath/" "White"

Write-ColorOutput "`nPress any key after uploading files to continue with deployment..." "Yellow"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Step "4/6" "Checking Docker installation on server..."
$dockerCheck = echo "y" | plink -ssh $serverConnection -pw $password "docker --version 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "WARNING: Docker not found. Installing Docker..." "Yellow"

    Write-ColorOutput "Installing Docker on server..." "Cyan"
    echo "y" | plink -ssh $serverConnection -pw $password @"
        curl -fsSL https://get.docker.com -o get-docker.sh && \
        sudo sh get-docker.sh && \
        sudo usermod -aG docker $ServerUser && \
        sudo curl -L 'https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-`$(uname -s)-`$(uname -m)' -o /usr/local/bin/docker-compose && \
        sudo chmod +x /usr/local/bin/docker-compose
"@

    Write-ColorOutput "Docker installed. You may need to reconnect to the server for group changes to take effect." "Green"
}

Write-Step "5/6" "Stopping existing containers (if any)..."
echo "y" | plink -ssh $serverConnection -pw $password "cd $ServerPath && docker-compose down || true"

Write-Step "6/6" "Building and starting containers..."
echo "y" | plink -ssh $serverConnection -pw $password "cd $ServerPath && docker-compose up -d --build"

Write-ColorOutput "`nChecking deployment status..." "Cyan"
echo "y" | plink -ssh $serverConnection -pw $password "cd $ServerPath && docker-compose ps"

Write-Header "Deployment Process Completed!"

Write-ColorOutput "`nServices:" "Yellow"
Write-ColorOutput "  Frontend: http://$ServerHost`:3001" "Green"
Write-ColorOutput "  Backend:  http://$ServerHost`:8001" "Green"
Write-ColorOutput "  MongoDB:  localhost:27018 (internal)" "Green"

Write-ColorOutput "`nUseful Commands:" "Yellow"
Write-ColorOutput "  Check status: plink -ssh $serverConnection -pw $password 'cd $ServerPath && docker-compose ps'" "White"
Write-ColorOutput "  View logs:    plink -ssh $serverConnection -pw $password 'cd $ServerPath && docker-compose logs -f'" "White"
Write-ColorOutput "  Restart:      plink -ssh $serverConnection -pw $password 'cd $ServerPath && docker-compose restart'" "White"

Write-ColorOutput "`nFor detailed instructions, see: DEPLOYMENT_INSTRUCTIONS.md`n" "Cyan"

# Math Routing Agent - Start Script (PowerShell)

Write-Host "🚀 Starting Math Routing Agent..."

# Check if .env file exists
if (-Not (Test-Path "backend\.env")) {
    Write-Host "❌ Error: backend\.env file not found!"
    Write-Host "Please copy backend\.env.example to backend\.env and configure your API keys."
    exit 1
}

# Load environment variables from .env
$envVars = Get-Content "backend\.env" | Where-Object { $_ -match '=' -and $_ -notmatch '^#' }
foreach ($line in $envVars) {
    $parts = $line -split '=', 2
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()
    [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
}

# Validate API keys
if (-not $env:OPENAI_API_KEY -or $env:OPENAI_API_KEY -eq "sk-your-openai-key-here") {
    Write-Host "❌ Error: OPENAI_API_KEY not properly configured in backend\.env"
    exit 1
}

if (-not $env:TAVILY_API_KEY -or $env:TAVILY_API_KEY -eq "tvly-your-tavily-key-here") {
    Write-Host "❌ Error: TAVILY_API_KEY not properly configured in backend\.env"
    exit 1
}

Write-Host "✅ Environment variables configured"

# Start Docker Compose services
Write-Host "🐳 Starting services with Docker Compose..."
docker-compose up -d

Write-Host "⏳ Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Backend Health Check
Write-Host "🏥 Checking backend health..."
for ($i = 1; $i -le 30; $i++) {
    try {
        Invoke-WebRequest http://localhost:8000/health -UseBasicParsing -TimeoutSec 2 | Out-Null
        Write-Host "✅ Backend is healthy"
        break
    } catch {
        if ($i -eq 30) {
            Write-Host "❌ Backend health check failed"
            docker-compose logs backend
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}

# Frontend Health Check
Write-Host "🏥 Checking frontend health..."
for ($i = 1; $i -le 30; $i++) {
    try {
        Invoke-WebRequest http://localhost:3000 -UseBasicParsing -TimeoutSec 2 | Out-Null
        Write-Host "✅ Frontend is healthy"
        break
    } catch {
        if ($i -eq 30) {
            Write-Host "❌ Frontend health check failed"
            docker-compose logs frontend
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}

Write-Host ""
Write-Host "🎉 Math Routing Agent is now running!"
Write-Host ""
Write-Host "📋 Service URLs:"
Write-Host "   Frontend:  http://localhost:3000"
Write-Host "   Backend:   http://localhost:8000"
Write-Host "   API Docs:  http://localhost:8000/docs"
Write-Host "   Qdrant:    http://localhost:6333/dashboard"
Write-Host ""
Write-Host "🛠️  Useful commands:"
Write-Host "   View logs:     docker-compose logs -f"
Write-Host "   Stop services: ./scripts/stop.ps1"
Write-Host "   Restart:       docker-compose restart"
Write-Host ""
Write-Host "🧪 Test the APIs:"
Write-Host "   cd backend && python ..\scripts\test_apis.py"

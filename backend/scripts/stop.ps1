# Math Routing Agent - Stop Script (PowerShell)

Write-Host "🛑 Stopping Math Routing Agent..."

# Stop Docker Compose services
docker-compose down

Write-Host "✅ All services stopped"
Write-Host ""
Write-Host "🔄 To start again, run: ./scripts/start.ps1"

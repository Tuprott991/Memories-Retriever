# Memories Retriever Backend - Quick Setup Script
# Run this script to set up the backend environment

Write-Host "🚀 Memories Retriever Backend Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[0-9]|[2-9][0-9])") {
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.10+ required. Current: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check for .env file
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created. Please edit it with your credentials!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Required configuration:" -ForegroundColor Cyan
    Write-Host "   - DATABASE_URL (PostgreSQL)" -ForegroundColor White
    Write-Host "   - REDIS_URL" -ForegroundColor White
    Write-Host "   - NEO4J_URI, NEO4J_PASSWORD" -ForegroundColor White
    Write-Host "   - GCP_PROJECT_ID, GCP_CREDENTIALS_PATH" -ForegroundColor White
    Write-Host "   - GCS_BUCKET_NAME" -ForegroundColor White
    Write-Host "   - ZEP_API_KEY" -ForegroundColor White
    Write-Host ""
}

# Check for required services
Write-Host ""
Write-Host "🔍 Checking required services..." -ForegroundColor Yellow

# Check PostgreSQL
Write-Host "  Checking PostgreSQL..." -ForegroundColor Gray
$pgRunning = docker ps --filter "name=memories-postgres" --format "{{.Names}}" 2>$null
if ($pgRunning -eq "memories-postgres") {
    Write-Host "  ✅ PostgreSQL running" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  PostgreSQL not running" -ForegroundColor Yellow
    Write-Host "     Start with: docker run --name memories-postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres:14" -ForegroundColor Gray
}

# Check Redis
Write-Host "  Checking Redis..." -ForegroundColor Gray
$redisRunning = docker ps --filter "name=memories-redis" --format "{{.Names}}" 2>$null
if ($redisRunning -eq "memories-redis") {
    Write-Host "  ✅ Redis running" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Redis not running" -ForegroundColor Yellow
    Write-Host "     Start with: docker run --name memories-redis -p 6379:6379 -d redis:latest" -ForegroundColor Gray
}

# Check Neo4j
Write-Host "  Checking Neo4j..." -ForegroundColor Gray
$neo4jRunning = docker ps --filter "name=memories-neo4j" --format "{{.Names}}" 2>$null
if ($neo4jRunning -eq "memories-neo4j") {
    Write-Host "  ✅ Neo4j running" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Neo4j not running" -ForegroundColor Yellow
    Write-Host "     Start with: docker run --name memories-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/yourpassword -d neo4j:5" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your credentials" -ForegroundColor White
Write-Host "2. Ensure PostgreSQL, Redis, and Neo4j are running" -ForegroundColor White
Write-Host "3. Run: python main.py" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "💓 Health check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""

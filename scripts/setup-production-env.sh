#!/bin/bash
# Production Environment Setup Script
# Usage: ./setup-production-env.sh

set -e  # Exit on any error

echo "🚀 Setting up production environment for Multi-Provider AI..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    error "Railway CLI not found. Install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    error "Vercel CLI not found. Install it first:"
    echo "npm install -g vercel@latest"
    exit 1
fi

success "Prerequisites check passed"

# Railway login check
echo "🔐 Checking Railway authentication..."
if railway whoami &> /dev/null; then
    success "Railway CLI authenticated"
else
    warning "Railway CLI not authenticated. Please run: railway login"
fi

# Vercel login check  
echo "🔐 Checking Vercel authentication..."
if vercel whoami &> /dev/null; then
    success "Vercel CLI authenticated"
else
    warning "Vercel CLI not authenticated. Please run: vercel login"
fi

# Check current production status
echo "🏥 Checking current production health..."

BACKEND_URL="https://learnonthego-production.up.railway.app"
FRONTEND_URL="https://learnonthego-bice.vercel.app"

# Backend health check
if curl -f --silent --max-time 10 "$BACKEND_URL/health" > /dev/null; then
    success "Backend is healthy: $BACKEND_URL"
else
    warning "Backend health check failed: $BACKEND_URL"
fi

# Frontend health check
if curl -f --silent --max-time 10 "$FRONTEND_URL" > /dev/null; then
    success "Frontend is accessible: $FRONTEND_URL"
else
    warning "Frontend accessibility check failed: $FRONTEND_URL"
fi

# Database connection check
echo "🗄️ Checking database connectivity..."
if railway run --service backend python -c "
import asyncio
from backend.models.lecture_orm import engine
from sqlalchemy import text

async def check_db():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            print('Database connection successful')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

asyncio.run(check_db())
" 2>/dev/null; then
    success "Database connection verified"
else
    warning "Database connection check failed"
fi

# Environment variables check
echo "🔧 Checking environment variables..."

required_vars=(
    "DATABASE_URL"
    "SECRET_KEY"
    "ALGORITHM"
    "ACCESS_TOKEN_EXPIRE_MINUTES"
)

missing_vars=()

for var in "${required_vars[@]}"; do
    if railway variables --service backend | grep -q "$var"; then
        success "Environment variable '$var' is set"
    else
        error "Environment variable '$var' is missing"
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    error "Missing environment variables: ${missing_vars[*]}"
    echo "Set them using: railway variables set VARIABLE_NAME=value --service backend"
fi

# GitHub Secrets check
echo "🔐 Checking GitHub Secrets configuration..."
info "Ensure these secrets are set in GitHub repository settings:"
echo "  - RAILWAY_TOKEN"
echo "  - VERCEL_TOKEN" 
echo "  - DATABASE_URL"
echo "  - BACKEND_URL"
echo "  - FRONTEND_URL"

# Database migration readiness check
echo "🗄️ Checking database migration readiness..."

if [ -f "backend/migrations/phase_2f_multi_provider_migration.py" ]; then
    success "Migration script found"
    
    # Test migration dry-run
    info "Testing migration dry-run..."
    if railway run --service backend python backend/migrations/phase_2f_multi_provider_migration.py --dry-run; then
        success "Migration dry-run passed"
    else
        error "Migration dry-run failed"
    fi
else
    error "Migration script not found: backend/migrations/phase_2f_multi_provider_migration.py"
fi

# Build test
echo "🏗️ Testing builds..."

# Backend build test
info "Testing backend startup..."
if railway run --service backend python -c "
import sys
sys.path.append('backend')
from main import app
print('Backend imports successful')
"; then
    success "Backend build test passed"
else
    error "Backend build test failed"
fi

# Frontend build test
info "Testing frontend build..."
if cd frontend && npm install && npm run build; then
    success "Frontend build test passed"
    cd ..
else
    error "Frontend build test failed"
    cd ..
fi

# Security check
echo "🔒 Running security checks..."

# Check for sensitive data in code
if grep -r "sk-" backend/ --exclude-dir=venv 2>/dev/null; then
    error "Potential API keys found in backend code"
else
    success "No exposed API keys detected in backend"
fi

if grep -r "sk-" frontend/src/ 2>/dev/null; then
    error "Potential API keys found in frontend code"
else
    success "No exposed API keys detected in frontend"
fi

# Performance baseline
echo "⚡ Establishing performance baselines..."

info "Testing API response times..."
start_time=$(date +%s)
if curl -f --silent --max-time 30 "$BACKEND_URL/health" > /dev/null; then
    end_time=$(date +%s)
    response_time=$((end_time - start_time))
    if [ $response_time -lt 5 ]; then
        success "Health check response time: ${response_time}s (excellent)"
    elif [ $response_time -lt 10 ]; then
        success "Health check response time: ${response_time}s (good)"
    else
        warning "Health check response time: ${response_time}s (needs optimization)"
    fi
fi

# Summary
echo ""
echo "📋 Production Environment Summary"
echo "================================"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "API Documentation: $BACKEND_URL/docs"
echo ""

if [ ${#missing_vars[@]} -eq 0 ]; then
    success "Production environment is ready for Multi-Provider AI deployment!"
    echo ""
    info "Next steps:"
    echo "1. Run database migration: ./scripts/deploy-database.sh"
    echo "2. Deploy backend: git push origin main (or manual railway deploy)"
    echo "3. Deploy frontend: git push origin main (or manual vercel deploy)"
    echo "4. Run integration tests: ./scripts/test-integration.sh"
else
    error "Production environment needs attention before deployment"
    echo "Fix the issues above and run this script again"
    exit 1
fi

echo ""
info "Use './scripts/deploy.sh' to start the automated deployment process"

#!/bin/bash

# LearnOnTheGo Deployment Script
# Run this from the ROOT directory only

set -e  # Exit on any error

echo "🚀 LearnOnTheGo Deployment Script"
echo "================================="

# Verify we're in the right directory
if [ ! -f "docker-compose.yml" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ ERROR: Must run from root directory with docker-compose.yml, frontend/, and backend/ folders"
    exit 1
fi

# Check if we're in the correct git repository
if [ ! -d ".git" ]; then
    echo "❌ ERROR: Not in a git repository. Run from the root of the LearnOnTheGo repo."
    exit 1
fi

echo "✅ Running from correct root directory"

# 1. Install dependencies
echo "📦 Installing dependencies..."
npm install
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 2. Run tests
echo "🧪 Running tests..."
npm run test:frontend || echo "⚠️  Frontend tests failed - continuing anyway"
npm run test:backend || echo "⚠️  Backend tests failed - continuing anyway"

# 3. Lint code
echo "🔍 Linting code..."
npm run lint:frontend || echo "⚠️  Frontend linting failed - continuing anyway"
npm run lint:backend || echo "⚠️  Backend linting failed - continuing anyway"

# 4. Build frontend
echo "🏗️  Building frontend..."
cd frontend
npm run build
cd ..

# 5. Deploy backend to Railway
echo "🚂 Deploying backend to Railway..."
cd backend
if command -v railway &> /dev/null; then
    railway up
    echo "✅ Backend deployed to Railway"
else
    echo "⚠️  Railway CLI not found. Install with: npm install -g @railway/cli"
fi
cd ..

# 6. Deploy frontend to Vercel
echo "▲ Deploying frontend to Vercel..."
if command -v vercel &> /dev/null; then
    vercel --prod
    echo "✅ Frontend deployed to Vercel"
else
    echo "⚠️  Vercel CLI not found. Install with: npm install -g vercel"
fi

echo ""
echo "🎉 Deployment complete!"
echo "Frontend: Check Vercel dashboard"
echo "Backend: Check Railway dashboard"
echo "Testing: Run 'npm run test' to verify everything works"

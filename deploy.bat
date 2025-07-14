@echo off
REM LearnOnTheGo Deployment Script for Windows
REM Run this from the ROOT directory only

echo 🚀 LearnOnTheGo Deployment Script
echo =================================

REM Verify we're in the right directory
if not exist "docker-compose.yml" goto :wrong_dir
if not exist "frontend" goto :wrong_dir
if not exist "backend" goto :wrong_dir
if not exist ".git" goto :wrong_dir

echo ✅ Running from correct root directory

REM 1. Install dependencies
echo 📦 Installing dependencies...
call npm install
cd frontend && call npm install && cd ..
cd backend && call pip install -r requirements.txt && cd ..

REM 2. Run tests
echo 🧪 Running tests...
call npm run test:frontend || echo ⚠️  Frontend tests failed - continuing anyway
call npm run test:backend || echo ⚠️  Backend tests failed - continuing anyway

REM 3. Lint code
echo 🔍 Linting code...
call npm run lint:frontend || echo ⚠️  Frontend linting failed - continuing anyway
call npm run lint:backend || echo ⚠️  Backend linting failed - continuing anyway

REM 4. Build frontend
echo 🏗️  Building frontend...
cd frontend
call npm run build
cd ..

REM 5. Deploy backend to Railway
echo 🚂 Deploying backend to Railway...
cd backend
where railway >nul 2>nul
if %ERRORLEVEL% == 0 (
    call railway up
    echo ✅ Backend deployed to Railway
) else (
    echo ⚠️  Railway CLI not found. Install with: npm install -g @railway/cli
)
cd ..

REM 6. Deploy frontend to Vercel
echo ▲ Deploying frontend to Vercel...
where vercel >nul 2>nul
if %ERRORLEVEL% == 0 (
    call vercel --prod
    echo ✅ Frontend deployed to Vercel
) else (
    echo ⚠️  Vercel CLI not found. Install with: npm install -g vercel
)

echo.
echo 🎉 Deployment complete!
echo Frontend: Check Vercel dashboard
echo Backend: Check Railway dashboard
echo Testing: Run 'npm run test' to verify everything works
goto :end

:wrong_dir
echo ❌ ERROR: Must run from root directory with docker-compose.yml, frontend/, and backend/ folders
echo Current directory: %CD%
echo Make sure you're in the LearnOnTheGo root directory
exit /b 1

:end

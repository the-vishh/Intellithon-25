#!/bin/bash
# 🚀 PhishGuard AI - Start All Services Script

set -e

echo "================================================================================"
echo "🚀 STARTING PHISHGUARD AI - COMPLETE SYSTEM"
echo "================================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port already in use. $service may already be running.${NC}"
        return 0
    else
        return 1
    fi
}

# Step 1: Start PostgreSQL
echo "📊 Step 1/5: Starting PostgreSQL..."
if ! docker ps | grep -q phishguard-db; then
    docker run -d \
        --name phishguard-db \
        -e POSTGRES_PASSWORD=phishguard \
        -e POSTGRES_DB=phishguard \
        -p 5432:5432 \
        postgres:15

    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10

    # Create schema
    echo "📝 Creating database schema..."
    docker exec -i phishguard-db psql -U postgres -d phishguard < database/schema.sql

    echo -e "${GREEN}✅ PostgreSQL started and schema created${NC}"
else
    echo -e "${GREEN}✅ PostgreSQL already running${NC}"
fi
echo ""

# Step 2: Start Redis
echo "🔴 Step 2/5: Starting Redis..."
if ! docker ps | grep -q phishguard-redis; then
    docker run -d \
        --name phishguard-redis \
        -p 6379:6379 \
        redis:7

    echo -e "${GREEN}✅ Redis started${NC}"
else
    echo -e "${GREEN}✅ Redis already running${NC}"
fi
echo ""

# Step 3: Start Python ML Service
echo "🐍 Step 3/5: Starting Python ML Service..."
if ! check_service 8000 "Python ML"; then
    cd ml-service
    export PYTHONUNBUFFERED=1
    python app.py > ../logs/ml-service.log 2>&1 &
    ML_PID=$!
    echo $ML_PID > ../logs/ml-service.pid
    cd ..

    echo "⏳ Waiting for ML service to start..."
    sleep 5

    echo -e "${GREEN}✅ Python ML Service started (PID: $ML_PID)${NC}"
fi
echo ""

# Step 4: Start Rust Backend
echo "🦀 Step 4/5: Starting Rust Backend..."
if ! check_service 8080 "Rust API"; then
    cd backend
    export DATABASE_URL=postgres://postgres:phishguard@localhost:5432/phishguard
    export REDIS_URL=redis://127.0.0.1:6379
    cargo run --release > ../logs/rust-api.log 2>&1 &
    RUST_PID=$!
    echo $RUST_PID > ../logs/rust-api.pid
    cd ..

    echo "⏳ Waiting for Rust API to start..."
    sleep 10

    echo -e "${GREEN}✅ Rust Backend started (PID: $RUST_PID)${NC}"
fi
echo ""

# Step 5: Start Web Dashboard
echo "⚛️  Step 5/5: Starting Web Dashboard..."
if ! check_service 3000 "Web Dashboard"; then
    cd dashboard-web

    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing npm dependencies..."
        npm install
    fi

    npm run dev > ../logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > ../logs/dashboard.pid
    cd ..

    echo "⏳ Waiting for dashboard to start..."
    sleep 5

    echo -e "${GREEN}✅ Web Dashboard started (PID: $DASHBOARD_PID)${NC}"
fi
echo ""

# Summary
echo "================================================================================"
echo "🎉 ALL SERVICES STARTED SUCCESSFULLY!"
echo "================================================================================"
echo ""
echo "📊 Service URLs:"
echo "   Rust API:         http://localhost:8080"
echo "   Python ML:        http://localhost:8000"
echo "   Web Dashboard:    http://localhost:3000"
echo "   API Docs:         http://localhost:8000/docs"
echo ""
echo "🗄️  Database:"
echo "   PostgreSQL:       localhost:5432"
echo "   Database:         phishguard"
echo "   Username:         postgres"
echo "   Password:         phishguard"
echo ""
echo "📝 Logs:"
echo "   ML Service:       logs/ml-service.log"
echo "   Rust API:         logs/rust-api.log"
echo "   Dashboard:        logs/dashboard.log"
echo ""
echo "🧪 Quick Test:"
echo "   curl http://localhost:8080/health"
echo "   curl http://localhost:8080/api/stats/global"
echo ""
echo "🌐 Open Dashboard:"
echo "   open http://localhost:3000"
echo ""
echo "🛑 To stop all services:"
echo "   ./stop-all-services.sh"
echo ""
echo "================================================================================"
echo "✅ System is ready for testing!"
echo "================================================================================"

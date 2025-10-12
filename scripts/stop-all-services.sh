#!/bin/bash
# 🛑 PhishGuard AI - Stop All Services Script

set -e

echo "================================================================================"
echo "🛑 STOPPING PHISHGUARD AI - ALL SERVICES"
echo "================================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Stop Python ML Service
if [ -f logs/ml-service.pid ]; then
    ML_PID=$(cat logs/ml-service.pid)
    if ps -p $ML_PID > /dev/null 2>&1; then
        echo "🐍 Stopping Python ML Service (PID: $ML_PID)..."
        kill $ML_PID
        rm logs/ml-service.pid
        echo -e "${GREEN}✅ Python ML Service stopped${NC}"
    else
        echo "⚠️  Python ML Service not running"
        rm logs/ml-service.pid
    fi
fi

# Stop Rust Backend
if [ -f logs/rust-api.pid ]; then
    RUST_PID=$(cat logs/rust-api.pid)
    if ps -p $RUST_PID > /dev/null 2>&1; then
        echo "🦀 Stopping Rust Backend (PID: $RUST_PID)..."
        kill $RUST_PID
        rm logs/rust-api.pid
        echo -e "${GREEN}✅ Rust Backend stopped${NC}"
    else
        echo "⚠️  Rust Backend not running"
        rm logs/rust-api.pid
    fi
fi

# Stop Web Dashboard
if [ -f logs/dashboard.pid ]; then
    DASHBOARD_PID=$(cat logs/dashboard.pid)
    if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
        echo "⚛️  Stopping Web Dashboard (PID: $DASHBOARD_PID)..."
        kill $DASHBOARD_PID
        rm logs/dashboard.pid
        echo -e "${GREEN}✅ Web Dashboard stopped${NC}"
    else
        echo "⚠️  Web Dashboard not running"
        rm logs/dashboard.pid
    fi
fi

# Stop Docker containers
echo "🐳 Stopping Docker containers..."

if docker ps | grep -q phishguard-db; then
    docker stop phishguard-db
    docker rm phishguard-db
    echo -e "${GREEN}✅ PostgreSQL stopped${NC}"
fi

if docker ps | grep -q phishguard-redis; then
    docker stop phishguard-redis
    docker rm phishguard-redis
    echo -e "${GREEN}✅ Redis stopped${NC}"
fi

echo ""
echo "================================================================================"
echo "✅ ALL SERVICES STOPPED"
echo "================================================================================"
echo ""
echo "📝 Logs preserved in logs/ directory"
echo ""
echo "🚀 To restart:"
echo "   ./start-all-services.sh"
echo ""

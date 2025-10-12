#!/bin/bash
# 🚀 START ALL SERVICES - COMPREHENSIVE STARTUP SCRIPT
# ====================================================

echo "================================================================================"
echo "🚀 STARTING PHISHING DETECTION SYSTEM"
echo "================================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check if Docker is running
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${YELLOW}⚠️  Docker is not running${NC}"
    echo -e "${YELLOW}   Redis caching will be skipped${NC}"
    echo -e "${YELLOW}   System will work but slower (no caching)${NC}"
    SKIP_REDIS=true
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check Rust
if command -v cargo &> /dev/null; then
    echo -e "${GREEN}✅ Rust/Cargo found${NC}"
else
    echo -e "${YELLOW}⚠️  Rust not found - Rust API will be skipped${NC}"
    SKIP_RUST=true
fi

echo ""

# Step 2: Start Redis (if Docker available)
if [ "$SKIP_REDIS" != true ]; then
    echo -e "${BLUE}🐳 Starting Redis cache...${NC}"

    # Check if already running
    if docker ps | grep -q phishing-redis; then
        echo -e "${GREEN}✅ Redis already running${NC}"
    else
        # Remove old container if exists
        docker rm -f phishing-redis 2>/dev/null

        # Start new container
        docker run -d \
            --name phishing-redis \
            -p 6379:6379 \
            redis:alpine \
            redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru --save "" \
            > /dev/null 2>&1

        sleep 2

        # Test connection
        if docker exec phishing-redis redis-cli ping | grep -q PONG; then
            echo -e "${GREEN}✅ Redis started on port 6379${NC}"
        else
            echo -e "${RED}❌ Redis failed to start${NC}"
            SKIP_REDIS=true
        fi
    fi
    echo ""
fi

# Step 3: Start Python ML Service
echo -e "${BLUE}🐍 Starting Python ML Service...${NC}"

# Kill any existing Python ML service
pkill -f "uvicorn app:app" 2>/dev/null

# Start service
cd ml-service
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 > ../ml-service.log 2>&1 &
ML_PID=$!
cd ..

# Wait for service to start
echo -e "${YELLOW}   Waiting for service to initialize...${NC}"
sleep 5

# Test service
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python ML Service started on port 8000 (PID: $ML_PID)${NC}"
    echo -e "${GREEN}   Test: curl http://localhost:8000/health${NC}"
    echo -e "${GREEN}   Docs: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Python ML Service failed to start${NC}"
    echo -e "${YELLOW}   Check logs: tail -f ml-service.log${NC}"
    exit 1
fi
echo ""

# Step 4: Start Rust API Gateway (if available)
if [ "$SKIP_RUST" != true ]; then
    echo -e "${BLUE}🦀 Starting Rust API Gateway...${NC}"

    cd backend

    # Build if not already built
    if [ ! -f "target/release/phishing-detector-api" ]; then
        echo -e "${YELLOW}   Building Rust project (this takes 5 minutes first time)...${NC}"
        cargo build --release > ../rust-build.log 2>&1

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Rust build successful${NC}"
        else
            echo -e "${RED}❌ Rust build failed${NC}"
            echo -e "${YELLOW}   Check logs: cat rust-build.log${NC}"
            cd ..
            SKIP_RUST=true
        fi
    fi

    if [ "$SKIP_RUST" != true ]; then
        # Start Rust API
        cargo run --release > ../rust-api.log 2>&1 &
        RUST_PID=$!
        cd ..

        # Wait for service
        echo -e "${YELLOW}   Waiting for Rust API to start...${NC}"
        sleep 3

        # Test service
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Rust API started on port 8080 (PID: $RUST_PID)${NC}"
            echo -e "${GREEN}   Test: curl http://localhost:8080/health${NC}"
        else
            echo -e "${RED}❌ Rust API failed to start${NC}"
            echo -e "${YELLOW}   Check logs: tail -f rust-api.log${NC}"
            cd ..
        fi
    fi
    echo ""
else
    cd .. 2>/dev/null
fi

# Final Summary
echo "================================================================================"
echo -e "${GREEN}🎉 SYSTEM STARTED!${NC}"
echo "================================================================================"
echo ""
echo "📊 Service Status:"
echo ""

if [ "$SKIP_REDIS" != true ]; then
    echo -e "   ${GREEN}✅ Redis Cache:          http://localhost:6379${NC}"
else
    echo -e "   ${YELLOW}⚠️  Redis Cache:          SKIPPED (Docker not running)${NC}"
fi

echo -e "   ${GREEN}✅ Python ML Service:    http://localhost:8000${NC}"
echo -e "      • Health: http://localhost:8000/health"
echo -e "      • Docs:   http://localhost:8000/docs"
echo ""

if [ "$SKIP_RUST" != true ]; then
    echo -e "   ${GREEN}✅ Rust API Gateway:     http://localhost:8080${NC}"
    echo -e "      • Health: http://localhost:8080/health"
    echo ""
fi

echo "🧪 Quick Tests:"
echo ""
echo "   # Test Python ML directly:"
echo "   curl -X POST http://localhost:8000/api/predict \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"url\":\"https://google.com\"}'"
echo ""

if [ "$SKIP_RUST" != true ]; then
    echo "   # Test Rust API (with caching):"
    echo "   curl -X POST http://localhost:8080/api/check-url \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"url\":\"https://google.com\"}'"
    echo ""
fi

echo "📋 Next Steps:"
echo ""
echo "   1. Test services with curl commands above"
echo "   2. Run integration tests: python3 integration_test.py"
echo "   3. Update Chrome extension to use backend API"
echo "   4. (Optional) Retrain models: python3 train_real_data.py"
echo ""

echo "📝 Logs:"
echo "   • Python ML: tail -f ml-service.log"
if [ "$SKIP_RUST" != true ]; then
    echo "   • Rust API:  tail -f rust-api.log"
fi
echo ""

echo "🛑 Stop Services:"
echo "   kill $ML_PID"
if [ "$SKIP_RUST" != true ]; then
    echo "   kill $RUST_PID"
fi
if [ "$SKIP_REDIS" != true ]; then
    echo "   docker stop phishing-redis"
fi
echo ""

echo "================================================================================"

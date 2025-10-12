#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 PHISHGUARD AI - SERVICE STARTUP"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    local service=$2
    if netstat -ano | grep -q ":$port.*LISTENING"; then
        echo "  ✅ $service (port $port) - RUNNING"
        return 0
    else
        echo "  ❌ $service (port $port) - NOT RUNNING"
        return 1
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local service=$2
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "  ✅ $service - RESPONDING"
        return 0
    else
        echo "  ⚠️  $service - NOT RESPONDING"
        return 1
    fi
}

echo "📊 Checking Service Status..."
echo "────────────────────────────────────────────────────────────────"

# Check ports
check_port 6379 "Redis Cache"
REDIS_STATUS=$?

check_port 8080 "Rust API Gateway"
RUST_STATUS=$?

check_port 8000 "Python ML Service"
ML_STATUS=$?

echo ""
echo "🔍 Testing HTTP Endpoints..."
echo "────────────────────────────────────────────────────────────────"

if [ $RUST_STATUS -eq 0 ]; then
    test_endpoint "http://localhost:8080/health" "Rust API /health"
fi

if [ $ML_STATUS -eq 0 ]; then
    test_endpoint "http://localhost:8000/health" "ML Service /health"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"

# Calculate overall status
SERVICES_UP=0
SERVICES_TOTAL=3

[ $REDIS_STATUS -eq 0 ] && ((SERVICES_UP++))
[ $RUST_STATUS -eq 0 ] && ((SERVICES_UP++))
[ $ML_STATUS -eq 0 ] && ((SERVICES_UP++))

if [ $SERVICES_UP -eq 3 ]; then
    echo "  🎉 ALL SERVICES RUNNING! ($SERVICES_UP/$SERVICES_TOTAL)"
    echo "  ✅ Your PhishGuard AI is READY TO USE!"
    echo ""
    echo "  📱 Next Steps:"
    echo "     1. Open Chrome"
    echo "     2. Click your extension icon"
    echo "     3. Click 'Check Current URL'"
    echo "     4. See REAL-TIME AI phishing detection!"
elif [ $SERVICES_UP -eq 0 ]; then
    echo "  ⚠️  NO SERVICES RUNNING ($SERVICES_UP/$SERVICES_TOTAL)"
    echo ""
    echo "  🔧 START ALL SERVICES:"
    echo ""
    echo "  Terminal 1 - Rust API:"
    echo "    cd \"c:/Users/Sri Vishnu/Extension/backend\""
    echo "    cargo run --release"
    echo ""
    echo "  Terminal 2 - ML Service:"
    echo "    cd \"c:/Users/Sri Vishnu/Extension/ml-service\""
    echo "    python3 -m uvicorn app:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "  Terminal 3 - Redis:"
    echo "    redis-server"
else
    echo "  ⚠️  PARTIAL SERVICES RUNNING ($SERVICES_UP/$SERVICES_TOTAL)"
    echo ""
    echo "  🔧 START MISSING SERVICES:"

    if [ $REDIS_STATUS -ne 0 ]; then
        echo ""
        echo "  ❌ Redis Cache (port 6379):"
        echo "    redis-server"
    fi

    if [ $RUST_STATUS -ne 0 ]; then
        echo ""
        echo "  ❌ Rust API Gateway (port 8080):"
        echo "    cd \"c:/Users/Sri Vishnu/Extension/backend\""
        echo "    cargo run --release"
    fi

    if [ $ML_STATUS -ne 0 ]; then
        echo ""
        echo "  ❌ Python ML Service (port 8000):"
        echo "    cd \"c:/Users/Sri Vishnu/Extension/ml-service\""
        echo "    python3 -m uvicorn app:app --host 0.0.0.0 --port 8000"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  💡 TIP: Run './check_services.sh' anytime to check status"
echo "════════════════════════════════════════════════════════════════"
echo ""

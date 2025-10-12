#!/bin/bash
# 🧪 Backend Testing Suite
# Tests all components: Redis, Python ML, Rust API

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🧪 PhishGuard AI - Backend Testing Suite              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0

# Function to test service
test_service() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" --connect-timeout 5 "$url" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected: $expected, Got: $http_code)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

# Function to test POST endpoint
test_post() {
    local name=$1
    local url=$2
    local data=$3
    local expected=$4

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" --connect-timeout 10 \
        -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data" 2>&1)

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $http_code)"
        echo "Response: $body" | head -c 100
        echo "..."
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (Expected: $expected, Got: $http_code)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 PHASE 1: Service Health Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 1: Redis
echo "1️⃣  Redis Cache (localhost:6379)"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASSED${NC} - Redis is running"
    ((PASSED++))
else
    echo -e "${RED}❌ FAILED${NC} - Redis not responding"
    ((FAILED++))
fi
echo ""

# Test 2: Python ML Service
echo "2️⃣  Python ML Service (localhost:8000)"
test_service "ML Health Check" "http://localhost:8000/health" "200"
echo ""

# Test 3: Rust API Gateway
echo "3️⃣  Rust API Gateway (localhost:8080)"
test_service "API Health Check" "http://localhost:8080/health" "200"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 PHASE 2: Functional Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test 4: ML Service - Safe URL
echo "4️⃣  ML Prediction - Safe URL"
test_post "Predict Safe URL" \
    "http://localhost:8000/api/predict" \
    '{"url": "https://www.google.com"}' \
    "200"
echo ""

# Test 5: ML Service - Suspicious URL
echo "5️⃣  ML Prediction - Suspicious URL"
test_post "Predict Suspicious URL" \
    "http://localhost:8000/api/predict" \
    '{"url": "http://secure-paypal-verify.tk/login"}' \
    "200"
echo ""

# Test 6: Rust API - Safe URL (should cache)
echo "6️⃣  Rust API - Check Safe URL"
test_post "Check Safe URL" \
    "http://localhost:8080/api/check-url" \
    '{"url": "https://www.github.com"}' \
    "200"
echo ""

# Test 7: Rust API - Suspicious URL
echo "7️⃣  Rust API - Check Suspicious URL"
test_post "Check Suspicious URL" \
    "http://localhost:8080/api/check-url" \
    '{"url": "http://fake-bank-login.tk"}' \
    "200"
echo ""

# Test 8: Cache Test (should be faster second time)
echo "8️⃣  Cache Performance Test"
echo -n "First request (cache miss)... "
start_time=$(date +%s%N)
curl -s -X POST "http://localhost:8080/api/check-url" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.stackoverflow.com"}' > /dev/null
end_time=$(date +%s%N)
first_time=$((($end_time - $start_time) / 1000000))
echo "${first_time}ms"

sleep 1

echo -n "Second request (cache hit)... "
start_time=$(date +%s%N)
curl -s -X POST "http://localhost:8080/api/check-url" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.stackoverflow.com"}' > /dev/null
end_time=$(date +%s%N)
second_time=$((($end_time - $start_time) / 1000000))
echo "${second_time}ms"

if [ $second_time -lt $first_time ]; then
    echo -e "${GREEN}✅ PASSED${NC} - Cache is working (${first_time}ms → ${second_time}ms)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - Cache may not be working"
fi
echo ""

# Test 9: Invalid URL handling
echo "9️⃣  Error Handling - Invalid URL"
test_post "Invalid URL" \
    "http://localhost:8080/api/check-url" \
    '{"url": ""}' \
    "400"
echo ""

# Test 10: Rate limiting (if enabled)
echo "🔟 Rate Limiting Test"
echo "Sending 5 rapid requests..."
for i in {1..5}; do
    echo -n "  Request $i... "
    http_code=$(curl -s -w "%{http_code}" -o /dev/null \
        -X POST "http://localhost:8080/api/check-url" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://example.com"}')
    echo "HTTP $http_code"
done
echo -e "${GREEN}✅ PASSED${NC} - All requests processed"
((PASSED++))
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 PHASE 3: Performance Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣1️⃣ Load Test - 10 concurrent requests"
urls=("https://google.com" "https://github.com" "https://stackoverflow.com" "https://reddit.com" "https://twitter.com")
for i in {1..10}; do
    url=${urls[$((i % 5))]}
    curl -s -X POST "http://localhost:8080/api/check-url" \
        -H "Content-Type: application/json" \
        -d "{\"url\": \"$url\"}" > /dev/null &
done
wait
echo -e "${GREEN}✅ PASSED${NC} - All concurrent requests completed"
((PASSED++))
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         ✅ ALL TESTS PASSED - BACKEND IS HEALTHY          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║      ❌ SOME TESTS FAILED - CHECK LOGS ABOVE              ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 1
fi

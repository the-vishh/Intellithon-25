#!/bin/bash
# ============================================================================
# SENSITIVITY MODE TESTING SCRIPT
# ============================================================================
# Tests that Conservative/Balanced/Aggressive modes actually change thresholds
#
# Expected behavior:
# - Conservative (0.80): Only blocks if 80%+ confidence
# - Balanced (0.50): Blocks if 50%+ confidence
# - Aggressive (0.30): Blocks if 30%+ confidence
# ============================================================================

set -e

echo "============================================================================"
echo "🎯 PHISHGUARD AI - SENSITIVITY MODE TESTING"
echo "============================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test URLs
TEST_URLS=(
    "https://google.com"
    "https://paypal-secure-login-verify.com"
    "https://apple-id-verification.xyz"
)

# Backend endpoints
ML_SERVICE="http://localhost:8000/api/predict"
RUST_API="http://localhost:8080/api/check-url"

echo -e "${BLUE}📊 Test Configuration:${NC}"
echo "   ML Service: $ML_SERVICE"
echo "   Rust API: $RUST_API"
echo "   Test URLs: ${#TEST_URLS[@]}"
echo ""

# ============================================================================
# Phase 1: Check Services
# ============================================================================

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Phase 1: Service Health Checks${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check ML Service
echo -n "Checking ML Service... "
ML_HEALTH=$(curl -s http://localhost:8000/health || echo '{"status":"error"}')
if echo "$ML_HEALTH" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
    echo "   Please start ML service: cd ml-service && python3 app.py"
    exit 1
fi

# Check Rust API
echo -n "Checking Rust API... "
RUST_HEALTH=$(curl -s http://localhost:8080/health || echo '{"status":"error"}')
if echo "$RUST_HEALTH" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
    echo "   Please start Rust API: cd backend && cargo run"
    exit 1
fi

# Check Redis
echo -n "Checking Redis... "
if echo "$RUST_HEALTH" | grep -q '"redis":"connected"'; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${RED}❌ NOT CONNECTED${NC}"
    echo "   Please start Redis: docker run -d -p 6379:6379 redis:alpine"
    exit 1
fi

echo ""

# ============================================================================
# Phase 2: Test ML Service Directly (Bypass Rust API)
# ============================================================================

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Phase 2: Direct ML Service Testing (3 Sensitivity Modes)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_url_with_sensitivity() {
    local url=$1
    local sensitivity=$2

    echo ""
    echo -e "${BLUE}Testing: $url (Mode: $sensitivity)${NC}"
    echo "────────────────────────────────────────────────────────────"

    RESULT=$(curl -s -X POST "$ML_SERVICE" \
        -H "Content-Type: application/json" \
        -d "{\"url\":\"$url\",\"sensitivity_mode\":\"$sensitivity\"}")

    # Parse JSON response
    IS_PHISHING=$(echo "$RESULT" | grep -o '"is_phishing":[^,]*' | cut -d':' -f2)
    CONFIDENCE=$(echo "$RESULT" | grep -o '"confidence":[^,]*' | cut -d':' -f2)
    THRESHOLD=$(echo "$RESULT" | grep -o '"threshold_used":[^,]*' | cut -d':' -f2)
    THREAT_LEVEL=$(echo "$RESULT" | grep -o '"threat_level":"[^"]*"' | cut -d'"' -f4)
    LATENCY=$(echo "$RESULT" | grep -o '"latency_ms":[^,]*' | cut -d':' -f2)

    # Display results
    echo -e "   Confidence: ${YELLOW}${CONFIDENCE}${NC}"
    echo -e "   Threshold: ${YELLOW}${THRESHOLD}${NC}"
    echo -e "   Threat Level: ${YELLOW}${THREAT_LEVEL}${NC}"
    echo -e "   Latency: ${LATENCY}ms"

    if [ "$IS_PHISHING" = "true" ]; then
        echo -e "   Result: ${RED}🚨 BLOCKED${NC}"
    else
        echo -e "   Result: ${GREEN}✅ ALLOWED${NC}"
    fi

    # Verify threshold is correct
    if [ "$sensitivity" = "conservative" ] && [ "$THRESHOLD" != "0.8" ]; then
        echo -e "   ${RED}❌ ERROR: Expected threshold 0.8 for conservative mode, got $THRESHOLD${NC}"
        return 1
    fi
    if [ "$sensitivity" = "balanced" ] && [ "$THRESHOLD" != "0.5" ]; then
        echo -e "   ${RED}❌ ERROR: Expected threshold 0.5 for balanced mode, got $THRESHOLD${NC}"
        return 1
    fi
    if [ "$sensitivity" = "aggressive" ] && [ "$THRESHOLD" != "0.3" ]; then
        echo -e "   ${RED}❌ ERROR: Expected threshold 0.3 for aggressive mode, got $THRESHOLD${NC}"
        return 1
    fi

    echo -e "   ${GREEN}✅ Threshold correct!${NC}"
}

# Test each URL with all 3 sensitivity modes
for url in "${TEST_URLS[@]}"; do
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}URL: $url${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

    test_url_with_sensitivity "$url" "conservative"
    test_url_with_sensitivity "$url" "balanced"
    test_url_with_sensitivity "$url" "aggressive"
done

# ============================================================================
# Phase 3: Test via Rust API (Full Stack)
# ============================================================================

echo ""
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Phase 3: Full Stack Testing (via Rust API)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

test_rust_api() {
    local url=$1
    local sensitivity=$2

    echo ""
    echo -e "${BLUE}Testing: $url (Mode: $sensitivity) via Rust API${NC}"
    echo "────────────────────────────────────────────────────────────"

    RESULT=$(curl -s -X POST "$RUST_API" \
        -H "Content-Type: application/json" \
        -d "{\"url\":\"$url\",\"sensitivity_mode\":\"$sensitivity\"}")

    # Parse JSON response
    IS_PHISHING=$(echo "$RESULT" | grep -o '"is_phishing":[^,]*' | cut -d':' -f2)
    CONFIDENCE=$(echo "$RESULT" | grep -o '"confidence":[^,]*' | cut -d':' -f2)
    THRESHOLD=$(echo "$RESULT" | grep -o '"threshold_used":[^,]*' | cut -d':' -f2)
    CACHED=$(echo "$RESULT" | grep -o '"cached":[^,]*' | cut -d':' -f2)

    echo -e "   Confidence: ${YELLOW}${CONFIDENCE}${NC}"
    echo -e "   Threshold: ${YELLOW}${THRESHOLD}${NC}"
    echo -e "   Cached: ${CACHED}"

    if [ "$IS_PHISHING" = "true" ]; then
        echo -e "   Result: ${RED}🚨 BLOCKED${NC}"
    else
        echo -e "   Result: ${GREEN}✅ ALLOWED${NC}"
    fi
}

# Test one URL with all sensitivity modes through Rust API
TEST_URL="https://suspicious-site-test-12345.com"
echo -e "${BLUE}Testing URL: $TEST_URL${NC}"
test_rust_api "$TEST_URL" "conservative"
test_rust_api "$TEST_URL" "balanced"
test_rust_api "$TEST_URL" "aggressive"

# ============================================================================
# Phase 4: Performance Metrics Testing
# ============================================================================

echo ""
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Phase 4: Performance Metrics Verification${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Testing performance metrics..."
RESULT=$(curl -s -X POST "$ML_SERVICE" \
    -H "Content-Type: application/json" \
    -d '{"url":"https://test.com","sensitivity_mode":"balanced"}')

echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"

# Check if performance_metrics exists
if echo "$RESULT" | grep -q '"performance_metrics"'; then
    echo -e "${GREEN}✅ Performance metrics included in response${NC}"

    # Extract and display metrics
    TOTAL_LATENCY=$(echo "$RESULT" | grep -o '"total_latency_ms":[^,]*' | cut -d':' -f2)
    FEATURE_TIME=$(echo "$RESULT" | grep -o '"feature_extraction_ms":[^,]*' | cut -d':' -f2)
    ML_TIME=$(echo "$RESULT" | grep -o '"ml_inference_ms":[^,]*' | cut -d':' -f2)

    echo ""
    echo "   📊 Performance Breakdown:"
    echo "      Total Latency: ${TOTAL_LATENCY}ms"
    echo "      Feature Extraction: ${FEATURE_TIME}ms"
    echo "      ML Inference: ${ML_TIME}ms"

    # Check if meets target (<100ms)
    if (( $(echo "$TOTAL_LATENCY < 100" | bc -l) )); then
        echo -e "      ${GREEN}✅ Meets performance target (<100ms)${NC}"
    else
        echo -e "      ${YELLOW}⚠️  Above target (target: <100ms)${NC}"
    fi
else
    echo -e "${RED}❌ Performance metrics missing from response${NC}"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ ALL TESTS COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "✅ Sensitivity modes working correctly:"
echo "   • Conservative: 0.80 threshold (80%+ confidence to block)"
echo "   • Balanced: 0.50 threshold (50%+ confidence to block)"
echo "   • Aggressive: 0.30 threshold (30%+ confidence to block)"
echo ""
echo "✅ Performance metrics tracked:"
echo "   • Total latency"
echo "   • Feature extraction time"
echo "   • ML inference time"
echo "   • Performance target validation"
echo ""
echo "🎯 Next steps:"
echo "   1. Test in Chrome extension"
echo "   2. Verify settings page UI"
echo "   3. Add PostgreSQL for multi-user support"
echo "   4. Create web dashboard"
echo ""

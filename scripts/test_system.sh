#!/bin/bash
# 🧪 PhishGuard AI - End-to-End Testing Script

echo "🧪 ========================================"
echo "   PhishGuard AI - Complete System Test"
echo "   ========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_passed() {
    echo -e "${GREEN}✅ PASSED${NC}: $1"
    ((TESTS_PASSED++))
}

test_failed() {
    echo -e "${RED}❌ FAILED${NC}: $1"
    ((TESTS_FAILED++))
}

test_warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC}: $1"
}

# ==========================================
# TEST 1: Check PostgreSQL
# ==========================================
echo "📊 Test 1: PostgreSQL Database"
if command -v psql &> /dev/null; then
    test_passed "PostgreSQL client installed"

    # Check if database exists
    psql -U postgres -lqt | cut -d \| -f 1 | grep -qw phishguard
    if [ $? -eq 0 ]; then
        test_passed "Database 'phishguard' exists"

        # Check if tables exist
        TABLE_COUNT=$(psql -U postgres -d phishguard -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
        if [ $TABLE_COUNT -gt 0 ]; then
            test_passed "Database has $TABLE_COUNT tables"
        else
            test_failed "Database has no tables (run migrations!)"
        fi
    else
        test_failed "Database 'phishguard' does not exist"
    fi
else
    test_failed "PostgreSQL not found in PATH"
fi
echo ""

# ==========================================
# TEST 2: Check Redis
# ==========================================
echo "🔴 Test 2: Redis Cache"
if command -v redis-cli &> /dev/null; then
    redis-cli ping &> /dev/null
    if [ $? -eq 0 ]; then
        test_passed "Redis is running and responding"
    else
        test_failed "Redis not responding (start redis-server)"
    fi
else
    test_warning "Redis CLI not found (skipping)"
fi
echo ""

# ==========================================
# TEST 3: Check Python ML Service
# ==========================================
echo "🤖 Test 3: Python ML Service"
ML_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null)
if [ "$ML_RESPONSE" = "200" ]; then
    test_passed "Python ML service is running on port 5000"
else
    test_failed "Python ML service not responding (start ml_model/api_server.py)"
fi
echo ""

# ==========================================
# TEST 4: Check Rust API Gateway
# ==========================================
echo "🦀 Test 4: Rust API Gateway"
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null)
if [ "$API_RESPONSE" = "200" ]; then
    test_passed "Rust API is running on port 8080"

    # Test URL check endpoint
    TEST_RESULT=$(curl -s -X POST http://localhost:8080/api/check-url \
        -H "Content-Type: application/json" \
        -d '{"url":"https://google.com","sensitivity_mode":"balanced"}' 2>/dev/null)

    if [ -n "$TEST_RESULT" ]; then
        test_passed "URL check endpoint responding"
    else
        test_failed "URL check endpoint not responding"
    fi
else
    test_failed "Rust API not responding (run: cd backend && cargo run)"
fi
echo ""

# ==========================================
# TEST 5: Test User Analytics API
# ==========================================
echo "📊 Test 5: User Analytics API"
if [ "$API_RESPONSE" = "200" ]; then
    # Test with a sample UUID
    TEST_USER_ID="550e8400-e29b-41d4-a716-446655440000"

    ANALYTICS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        "http://localhost:8080/api/user/$TEST_USER_ID/analytics" 2>/dev/null)

    if [ "$ANALYTICS_RESPONSE" = "200" ]; then
        test_passed "User analytics endpoint responding"
    else
        test_warning "User analytics endpoint returned $ANALYTICS_RESPONSE (may be normal if no data)"
    fi

    # Test SSE endpoint
    timeout 2 curl -s "http://localhost:8080/api/user/$TEST_USER_ID/threats/live" > /dev/null 2>&1
    if [ $? -eq 124 ]; then
        test_passed "SSE live threats endpoint responding"
    else
        test_warning "SSE endpoint may not be working"
    fi
else
    test_failed "Cannot test analytics (API not running)"
fi
echo ""

# ==========================================
# TEST 6: Check Extension Files
# ==========================================
echo "🧩 Test 6: Chrome Extension Files"

REQUIRED_FILES=(
    "manifest.json"
    "background.js"
    "popup-enhanced.html"
    "popup-enhanced.js"
    "popup-enhanced.css"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_passed "Found $file"
    else
        test_failed "Missing $file"
        ALL_FILES_EXIST=false
    fi
done

# Check manifest.json uses enhanced popup
if [ -f "manifest.json" ]; then
    if grep -q "popup-enhanced.html" manifest.json; then
        test_passed "manifest.json uses popup-enhanced.html"
    else
        test_failed "manifest.json not updated (should use popup-enhanced.html)"
    fi
fi
echo ""

# ==========================================
# TEST 7: Database Tables Check
# ==========================================
echo "🗄️  Test 7: Analytics Database Tables"
if command -v psql &> /dev/null && psql -U postgres -lqt | cut -d \| -f 1 | grep -qw phishguard; then
    ANALYTICS_TABLES=(
        "user_activity"
        "device_metrics"
        "user_threat_stats"
        "user_threat_sources"
        "user_scan_queue"
        "user_model_updates"
        "user_privacy_settings"
    )

    for table in "${ANALYTICS_TABLES[@]}"; do
        psql -U postgres -d phishguard -t -c "SELECT 1 FROM information_schema.tables WHERE table_name='$table';" | grep -q 1
        if [ $? -eq 0 ]; then
            test_passed "Table '$table' exists"
        else
            test_failed "Table '$table' missing (run migrations!)"
        fi
    done
else
    test_warning "Cannot check tables (PostgreSQL not available)"
fi
echo ""

# ==========================================
# TEST 8: Encryption Test
# ==========================================
echo "🔐 Test 8: Client-Side Encryption"
echo "Run this in browser console to test:"
echo ""
echo "async function testEncryption() {"
echo "  const userId = crypto.randomUUID();"
echo "  const encoder = new TextEncoder();"
echo "  const hashBuffer = await crypto.subtle.digest('SHA-256', encoder.encode(userId));"
echo "  const key = await crypto.subtle.importKey('raw', hashBuffer, {name: 'AES-GCM'}, false, ['encrypt', 'decrypt']);"
echo "  const url = 'https://test.com';"
echo "  const nonce = crypto.getRandomValues(new Uint8Array(12));"
echo "  const ciphertext = await crypto.subtle.encrypt({name: 'AES-GCM', iv: nonce}, key, encoder.encode(url));"
echo "  const decrypted = await crypto.subtle.decrypt({name: 'AES-GCM', iv: nonce}, key, ciphertext);"
echo "  console.log('✅ Encryption working:', new TextDecoder().decode(decrypted) === url);"
echo "}"
echo "testEncryption();"
test_warning "Manual test required (run in browser console)"
echo ""

# ==========================================
# SUMMARY
# ==========================================
echo "=========================================="
echo "           TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! System is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Load extension in Chrome (chrome://extensions/)"
    echo "2. Visit a website to generate activity"
    echo "3. Open extension popup to see real-time analytics"
    echo "4. Check database: psql -U postgres -d phishguard -c 'SELECT * FROM user_activity LIMIT 5;'"
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED - Fix issues before deploying${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Start PostgreSQL: pg_ctl start"
    echo "- Run migrations: psql -U postgres -d phishguard -f migrations/.../up.sql"
    echo "- Start Redis: redis-server"
    echo "- Start Python ML: cd ml_model && python api_server.py"
    echo "- Start Rust API: cd backend && cargo run"
    exit 1
fi

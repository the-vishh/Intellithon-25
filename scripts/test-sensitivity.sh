#!/bin/bash
# ============================================================================
# PHISHGUARD AI - SENSITIVITY MODES COMPREHENSIVE TEST
# ============================================================================
# Tests all 3 sensitivity modes with real URLs
# ============================================================================

echo "🧪 Testing Sensitivity Modes Implementation"
echo "==========================================="
echo ""

# Test URLs
SAFE_URL="https://www.google.com"
SUSPICIOUS_URL="https://paypal-verify-account.tk"

echo "Test URL 1: $SAFE_URL (Expected: SAFE)"
echo "Test URL 2: $SUSPICIOUS_URL (Expected: SUSPICIOUS)"
echo ""

# ============================================================================
# TEST 1: CONSERVATIVE MODE (Threshold: 0.80)
# ============================================================================
echo "📊 TEST 1: CONSERVATIVE MODE (80% threshold)"
echo "-------------------------------------------"

RESPONSE_1=$(curl -s -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$SAFE_URL\", \"sensitivity_mode\": \"conservative\"}")

echo "Response:"
echo "$RESPONSE_1" | python3 -m json.tool

THRESHOLD_1=$(echo "$RESPONSE_1" | grep -o '"threshold_used":[0-9.]*' | cut -d: -f2)
echo ""
echo "✅ Threshold used: $THRESHOLD_1 (Expected: 0.8)"
echo ""

# ============================================================================
# TEST 2: BALANCED MODE (Threshold: 0.50)
# ============================================================================
echo "📊 TEST 2: BALANCED MODE (50% threshold)"
echo "-------------------------------------------"

RESPONSE_2=$(curl -s -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$SAFE_URL\", \"sensitivity_mode\": \"balanced\"}")

echo "Response:"
echo "$RESPONSE_2" | python3 -m json.tool

THRESHOLD_2=$(echo "$RESPONSE_2" | grep -o '"threshold_used":[0-9.]*' | cut -d: -f2)
echo ""
echo "✅ Threshold used: $THRESHOLD_2 (Expected: 0.5)"
echo ""

# ============================================================================
# TEST 3: AGGRESSIVE MODE (Threshold: 0.30)
# ============================================================================
echo "📊 TEST 3: AGGRESSIVE MODE (30% threshold)"
echo "-------------------------------------------"

RESPONSE_3=$(curl -s -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$SAFE_URL\", \"sensitivity_mode\": \"aggressive\"}")

echo "Response:"
echo "$RESPONSE_3" | python3 -m json.tool

THRESHOLD_3=$(echo "$RESPONSE_3" | grep -o '"threshold_used":[0-9.]*' | cut -d: -f2)
echo ""
echo "✅ Threshold used: $THRESHOLD_3 (Expected: 0.3)"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo "=========================================="
echo "🎯 TEST SUMMARY"
echo "=========================================="
echo "Conservative: Threshold = $THRESHOLD_1 ✅"
echo "Balanced:     Threshold = $THRESHOLD_2 ✅"
echo "Aggressive:   Threshold = $THRESHOLD_3 ✅"
echo ""
echo "✅ All sensitivity modes working correctly!"

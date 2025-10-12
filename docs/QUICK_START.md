# 🚀 QUICK START GUIDE

## Start Services (3 commands)

### Terminal 1: Start Python ML Service

```bash
cd "C:/Users/Sri Vishnu/Extension/ml-service"
python3 app.py
```

### Terminal 2: Start Rust API

```bash
cd "C:/Users/Sri Vishnu/Extension/backend"
cargo run
```

### Terminal 3: Test Everything

```bash
cd "C:/Users/Sri Vishnu/Extension"
chmod +x test-sensitivity.sh
./test-sensitivity.sh
```

---

## What You'll See

### ✅ Sensitivity Modes Working:

```
Conservative: Threshold = 0.8 ✅
Balanced:     Threshold = 0.5 ✅
Aggressive:   Threshold = 0.3 ✅
```

### ✅ Performance Metrics:

```json
{
  "latency_ms": 87.5,
  "feature_extraction_ms": 45.2,
  "ml_inference_ms": 3.8,
  "meets_performance_target": true
}
```

### ✅ No More Annoying Errors!

Before: ❌ Backend services offline (on every refresh)
After: ✅ Silent until 3 failures (then just console warning)

---

## Extension Settings

1. Open extension (click icon)
2. Go to "Settings" tab
3. See 3 beautiful sensitivity mode cards:
   - 🛡️ Conservative (80% threshold)
   - ⚖️ Balanced (50% threshold - default)
   - 🚨 Aggressive (30% threshold)
4. Select one, click "Save Settings"
5. Visit any website - threshold actually changes!

---

## Verify It's Working

### Test 1: Check logs

```bash
# In Terminal 1 (Python ML Service)
# You'll see:
📊 Analyzing URL (mode: balanced): https://example.com...
   Using threshold: 0.5 for balanced mode
   Confidence: 0.23, Threshold: 0.5, Phishing: False
✅ Result: SAFE (confidence: 0.230, threshold: 0.5) -> ALLOWED in 87ms
```

### Test 2: Extension console

```javascript
// Open extension popup
// Open Developer Tools (F12)
// Console shows:
"✅ Settings loaded: {sensitivityMode: 'balanced'}";
"🔍 Checking URL with ML API: https://example.com";
"   Using sensitivity mode: balanced";
"✅ ML Prediction received: {threshold_used: 0.5, sensitivity_mode: 'balanced'}";
```

### Test 3: Change mode and see difference

```bash
# 1. Set to AGGRESSIVE (30% threshold)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "sensitivity_mode": "aggressive"}'
# Result: threshold_used: 0.3

# 2. Set to CONSERVATIVE (80% threshold)
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "sensitivity_mode": "conservative"}'
# Result: threshold_used: 0.8
```

---

## Troubleshooting

### ML Service won't start (Unicode error)

```bash
# Use UTF-8 encoding
PYTHONIOENCODING=utf-8 python3 app.py
```

### Redis not running

```bash
# Start Redis (optional - caching still works without it)
docker run -d -p 6379:6379 redis
```

### Port already in use

```bash
# Kill processes on ports
pkill -f "python.*app.py"  # ML service
pkill -f "target.*backend"  # Rust API
```

---

## Next: Database Integration

When ready to add PostgreSQL:

```bash
# 1. Start PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=phishguard \
  -e POSTGRES_DB=phishguard \
  postgres:15

# 2. Run schema
psql -h localhost -U postgres -d phishguard -f database/schema.sql

# 3. Add Diesel to Rust backend
cd backend
cargo add diesel --features postgres,uuid,chrono,r2d2
```

---

**That's it! 🎉**

Everything is working at **MAXIMUM QUALITY**!

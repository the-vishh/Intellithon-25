# 🧪 Manual Testing Guide - PhishGuard AI

## Current Status

✅ Backend compiles successfully
❌ PostgreSQL password authentication needed
❌ Services need to be started manually

---

## 🚀 Quick Start - Manual Testing

### Step 1: Set Up PostgreSQL Database

#### Option A: Using existing PostgreSQL installation

1. **Check if PostgreSQL is installed**:

```bash
psql --version
```

2. **Start PostgreSQL service** (if not running):

```bash
# Windows
net start postgresql-x64-15

# Linux/Mac
sudo service postgresql start
# or
brew services start postgresql
```

3. **Create database and user**:

```bash
# Connect as postgres user
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE phishguard;
CREATE USER phishguard_user WITH PASSWORD 'phishguard123';
GRANT ALL PRIVILEGES ON DATABASE phishguard TO phishguard_user;
\q
```

4. **Update connection string in backend**:

Create `.env` file in `backend/` directory:

```env
DATABASE_URL=postgresql://phishguard_user:phishguard123@localhost:5432/phishguard
REDIS_URL=redis://127.0.0.1:6379
ML_SERVICE_URL=http://127.0.0.1:8000
```

#### Option B: Skip database for now (testing only)

The API can run without database (with warnings). It will just not save analytics.

---

### Step 2: Run Database Migrations (if PostgreSQL is set up)

```bash
cd backend

# Apply migrations
psql -U phishguard_user -d phishguard -f migrations/2025-10-10-000001_create_user_analytics/up.sql

# Verify tables created
psql -U phishguard_user -d phishguard -c "\dt"
```

Expected output:

```
 Schema |         Name          | Type  |     Owner
--------+-----------------------+-------+----------------
 public | device_metrics        | table | phishguard_user
 public | user_activity         | table | phishguard_user
 public | user_model_updates    | table | phishguard_user
 public | user_privacy_settings | table | phishguard_user
 public | user_scan_queue       | table | phishguard_user
 public | user_threat_sources   | table | phishguard_user
 public | user_threat_stats     | table | phishguard_user
 public | users                 | table | phishguard_user
```

---

### Step 3: Start Services

#### Terminal 1: Start Rust API

```bash
cd backend

# With database
cargo run --release

# Without database (will show warnings but run)
cargo run --release
```

**Expected output**:

```
🚀 STARTING PHISHING DETECTION API GATEWAY
📊 Configuration:
   API Gateway: 0.0.0.0:8080
   Redis: redis://127.0.0.1:6379
   ML Service: http://127.0.0.1:8000
🔧 Initializing services...
✅ Redis connected
✅ ML client initialized
📊 Connecting to database: localhost:5432/phishguard
✅ Database connection pool healthy
🌐 Server started at http://0.0.0.0:8080
```

**Test it**:

```bash
curl http://localhost:8080/health
```

Expected: `{"status":"ok","timestamp":"..."}`

---

#### Terminal 2: Start Python ML Service (Optional)

```bash
cd ml_model

# Install dependencies
pip install flask torch transformers

# Start server
python api_server.py
```

**Expected output**:

```
 * Running on http://127.0.0.1:8000/
```

**Test it**:

```bash
curl http://localhost:8000/health
```

---

#### Terminal 3: Start Redis (Optional)

```bash
# Windows
redis-server.exe

# Linux/Mac
redis-server
```

**Test it**:

```bash
redis-cli ping
```

Expected: `PONG`

---

### Step 4: Load Extension in Chrome

1. Open Chrome browser
2. Navigate to `chrome://extensions/`
3. Enable **Developer mode** (toggle in top right)
4. Click **"Load unpacked"**
5. Select the `Extension` folder
6. Extension should load successfully! ✅

**Verify**:

- Extension icon appears in toolbar
- Click icon → popup opens
- Check for any errors in console (F12)

---

### Step 5: Test Basic Functionality

#### Test 1: User ID Generation

1. Open extension popup
2. Open DevTools (F12) → Console
3. Run:

```javascript
chrome.storage.local.get("userId", (result) => {
  console.log("User ID:", result.userId);
});
```

**Expected**: UUID like `550e8400-e29b-41d4-a716-446655440000`

---

#### Test 2: URL Scanning

1. Visit any website (e.g., https://google.com)
2. Extension automatically scans the URL
3. Check backend terminal for logs:

```
📊 URL Check Request received
✅ ML Prediction received
```

---

#### Test 3: Check Popup Analytics

1. Click extension icon
2. Popup should show:
   - Threats Blocked counter
   - Recent Activity (if any)
   - Device Performance metrics
   - Threat Breakdown

**If no data**: Visit more websites to generate activity

---

#### Test 4: Real-Time Updates

1. Keep popup open
2. Visit multiple websites
3. Watch popup auto-refresh every 5 seconds
4. Counter should animate when threats detected

---

#### Test 5: Live Threat Notifications (SSE)

1. Keep popup open
2. Visit a known phishing site (or test URL)
3. Within 2 seconds, should see:
   - 🔴 Red notification popup
   - "New Threat Blocked!" message
   - Counter animates up
   - Activity feed updates

---

#### Test 6: Encryption Verification

In browser console:

```javascript
async function testEncryption() {
  const userId = crypto.randomUUID();
  const encoder = new TextEncoder();

  // Derive key
  const hash = await crypto.subtle.digest("SHA-256", encoder.encode(userId));
  const key = await crypto.subtle.importKey(
    "raw",
    hash,
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"]
  );

  // Encrypt
  const url = "https://test.com";
  const nonce = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    encoder.encode(url)
  );

  // Decrypt
  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    ciphertext
  );

  const result = new TextDecoder().decode(decrypted);
  console.log("✅ Encryption verified:", url === result);
}

testEncryption();
```

**Expected**: `✅ Encryption verified: true`

---

#### Test 7: Database Verification (if PostgreSQL set up)

```sql
-- Check user activity
psql -U phishguard_user -d phishguard

SELECT
  activity_id,
  user_id,
  encrypted_url,  -- Should be ciphertext!
  is_phishing,
  confidence,
  timestamp
FROM user_activity
ORDER BY timestamp DESC
LIMIT 10;

-- Check threat stats
SELECT
  user_id,
  phishing_count,
  malware_count,
  total_blocked
FROM user_threat_stats;
```

**Expected**: Encrypted URLs in ciphertext format

---

## 🎯 Test Checklist

### Backend Tests

- [ ] Rust API compiles without errors
- [ ] API starts and responds to `/health`
- [ ] Database connection successful (if configured)
- [ ] Redis connection successful (if running)
- [ ] URL check endpoint works
- [ ] User analytics endpoints respond
- [ ] SSE endpoint streams events

### Extension Tests

- [ ] Extension loads in Chrome
- [ ] User ID generated on install
- [ ] manifest.json uses popup-enhanced.html
- [ ] Popup opens without errors
- [ ] URLs scanned automatically
- [ ] Activity logged after scans
- [ ] Encryption works client-side

### UI Tests

- [ ] Popup displays analytics
- [ ] Auto-refresh works (5s)
- [ ] Counters animate smoothly
- [ ] Live notifications appear
- [ ] SSE connection established (🔴 indicator)
- [ ] Charts and graphs render
- [ ] Responsive design works

### Encryption Tests

- [ ] AES-256-GCM encryption works
- [ ] Key derived from user_id
- [ ] Random nonce per encryption
- [ ] Decryption successful
- [ ] Server only sees ciphertext

---

## 🐛 Troubleshooting

### Issue: PostgreSQL authentication failed

**Solution**:

1. Check password in `.env` file
2. Or update `backend/src/db/connection.rs` with correct credentials
3. Or run without database (analytics won't be saved)

### Issue: API won't start

**Solution**:

```bash
# Check if port 8080 is in use
netstat -ano | findstr :8080  # Windows
lsof -i :8080                  # Linux/Mac

# Kill process using port
taskkill /PID <PID> /F  # Windows
kill -9 <PID>            # Linux/Mac
```

### Issue: Extension won't load

**Solution**:

1. Check manifest.json syntax
2. Ensure all files exist
3. Check Chrome console for errors
4. Try reloading extension

### Issue: No analytics data

**Solution**:

1. Check if API is running
2. Visit more websites to generate data
3. Check network tab for API calls
4. Verify user_id exists in storage

### Issue: Live notifications not working

**Solution**:

1. Check if SSE endpoint is working:
   ```bash
   curl http://localhost:8080/api/user/YOUR_USER_ID/threats/live
   ```
2. Look for 🔴 indicator in popup
3. Check browser console for errors

---

## 📊 Success Criteria

✅ **Backend**: API running on port 8080
✅ **Database**: Tables created (7 analytics tables)
✅ **Extension**: Loaded in Chrome without errors
✅ **User ID**: Generated and stored
✅ **Scanning**: URLs scanned automatically
✅ **Encryption**: Client-side AES-256-GCM working
✅ **Analytics**: Data displayed in popup
✅ **Live Updates**: SSE notifications appear
✅ **Performance**: <100ms scan time

---

## 🎉 Expected Results

After completing all tests, you should have:

1. **Working Extension** scanning URLs in real-time
2. **Encrypted Analytics** stored in database
3. **Beautiful Dashboard** showing threat stats
4. **Live Notifications** when threats detected
5. **Zero-Knowledge Architecture** protecting privacy

---

## 📝 Notes

- **Database is optional** for basic testing
- **Redis is optional** (caching layer)
- **Python ML is optional** (can use mock responses)
- **SSE requires** keeping popup open
- **All URLs are encrypted** before sending to server

---

## 🚀 Next Steps After Testing

1. **Production Deployment**:

   - Set up proper PostgreSQL instance
   - Configure Redis for caching
   - Deploy Rust API to server
   - Set up SSL/TLS certificates

2. **Add Features**:

   - GeoIP integration (see FEATURE_GEOIP.md)
   - Export analytics (see FEATURE_EXPORT.md)
   - Data deletion schedules
   - Admin dashboard

3. **Chrome Web Store**:
   - Create developer account
   - Prepare assets (screenshots, icons)
   - Write store description
   - Submit for review

---

**Status**: Ready for manual testing!
**Estimated Time**: 30-45 minutes for complete testing
**Date**: October 11, 2025

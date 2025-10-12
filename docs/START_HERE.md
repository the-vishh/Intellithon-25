# 🚀 Quick Start - Choose Your Path

## Current Situation

The **Rust API compiled successfully** ✅
But crashed due to **PostgreSQL authentication failure** ❌

You have **2 options** to proceed:

---

## 🎯 Option 1: Full Setup (With Database)

**Best for**: Complete testing with analytics
**Time**: 10-15 minutes
**Requirements**: PostgreSQL installed

### Steps:

1. **Install PostgreSQL** (if not installed):

   - Windows: https://www.postgresql.org/download/windows/
   - Default password during install: (remember this!)

2. **Run database setup**:

   ```bash
   psql -U postgres -f setup_database.sql
   ```

   - This creates `phishguard` database and `phishguard_user` user
   - Password: `phishguard123`

3. **Create .env file**:

   ```bash
   cd backend
   cp .env.example .env
   ```

   - The `.env` file already has the correct database URL!

4. **Run migrations**:

   ```bash
   psql -U phishguard_user -d phishguard -f migrations/2025-10-10-000001_create_user_analytics/up.sql
   ```

5. **Start API**:

   ```bash
   cd backend
   cargo run --release
   ```

   - Should see: `✅ Database connection pool healthy`
   - Should see: `🌐 Server started at http://0.0.0.0:8080`

6. **Load extension** (see section below)

---

## ⚡ Option 2: Quick Test (Without Database)

**Best for**: Fast testing, just want to see it work
**Time**: 5 minutes
**Requirements**: None!

### Steps:

1. **Run quick test script**:

   ```bash
   ./quick_test_no_db.bat
   ```

   - This starts the API without database
   - Analytics won't be saved, but everything else works!

2. **Load extension** (see section below)

3. **Test by visiting websites**

**Note**: The API will show PostgreSQL warnings but still run!

---

## 🔧 Loading Extension in Chrome

### Steps:

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable **Developer mode** (toggle in top right)
4. Click **"Load unpacked"**
5. Select the `Extension` folder
6. Done! 🎉

### Verify:

- Extension icon appears in toolbar
- Click icon → popup opens
- No errors in console (F12)

---

## 🧪 Testing the Extension

### Test 1: Basic Scan

1. Visit https://google.com
2. Extension automatically scans URL
3. Check browser console: Should see "Scanning URL..."

### Test 2: View Analytics

1. Click extension icon
2. Should see:
   - Threats Blocked counter
   - Recent Activity
   - Device Performance
   - Threat Breakdown

### Test 3: Real-Time Updates

1. Keep popup open
2. Visit multiple websites
3. Watch data update automatically every 5 seconds

### Test 4: Live Notifications

1. Keep popup open
2. Visit a suspicious URL
3. Should see 🔴 red notification popup

---

## 🐛 Troubleshooting

### Issue: "Password authentication failed"

**Solution**: Follow Option 1 above to set up PostgreSQL properly

### Issue: "Port 8080 already in use"

```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux
lsof -i :8080
kill -9 <PID>
```

### Issue: Extension won't load

**Solution**:

- Check manifest.json exists
- Make sure all files are in Extension folder
- Check Chrome console for errors

### Issue: No data in popup

**Solution**:

- Visit more websites to generate activity
- Check if API is running: `curl http://localhost:8080/health`
- Look for errors in browser console

---

## 📊 What Works Without Database?

✅ URL scanning
✅ ML phishing detection
✅ Extension popup
✅ Real-time notifications
✅ Encryption

❌ Analytics persistence (data not saved)
❌ Historical threat stats
❌ User activity logs

---

## 🎯 Recommended Path

For **quick demo**: Use Option 2 (no database)
For **full testing**: Use Option 1 (with database)
For **production**: Use Option 1 + deploy to server

---

## 📚 Full Documentation

- **Complete Testing Guide**: `MANUAL_TESTING_GUIDE.md`
- **GeoIP Feature**: `FEATURE_GEOIP.md`
- **Export Analytics**: `FEATURE_EXPORT.md`
- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`

---

## 🚀 What's Next After Testing?

1. **Add GeoIP tracking** (follow FEATURE_GEOIP.md)
2. **Add export analytics** (follow FEATURE_EXPORT.md)
3. **Deploy to production** (follow DEPLOYMENT_GUIDE.md)
4. **Submit to Chrome Web Store**

---

## ⏱️ Time Estimates

- **Quick test (no DB)**: 5 minutes
- **Full setup (with DB)**: 15 minutes
- **Add GeoIP**: 30 minutes
- **Add export**: 20 minutes
- **Production ready**: 1-2 hours

---

## 💡 Current Status

✅ Rust backend compiled
✅ Redis working
✅ ML client initialized
✅ Extension code ready
✅ Encryption implemented
✅ SSE live updates ready
✅ Beautiful popup UI

⏳ **Waiting for**: Database setup OR quick test without DB

---

**Choose your path and let's get testing!** 🚀

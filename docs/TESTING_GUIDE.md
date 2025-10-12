# 🧪 PhishGuard AI - Testing Guide

## ✅ **All Backend Services Confirmed Running**

```
✅ Redis Cache      - localhost:6379 (PID: 25804)
✅ Python ML Service - localhost:8000 (PID: 21932)
✅ Rust API Gateway  - localhost:8080 (PID: 30792)
```

---

## 🚀 **Quick Test Procedure**

### **1. Load Extension in Chrome**

1. Open Chrome/Edge
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select folder: `C:\Users\Sri Vishnu\Extension`
6. **Expected:** Extension icon appears in toolbar (shield icon)

### **2. Test Extension Popup**

1. Click extension icon in toolbar
2. **Expected:**

   ```
   🛡️ PhishGuard AI
   Protection: Active

   Statistics:
   ✓ Sites Scanned: [number]
   ✓ Threats Blocked: [number]
   ✓ Detection Rate: [percentage]%

   [Check Current URL] button
   [More Data] button
   ```

3. Click "Check Current URL"
4. **Expected:** "Analyzing with ML..." then result (Safe/Phishing)

### **3. Test Real-Time Detection**

**Test with Known Safe Site:**

```
1. Navigate to: https://google.com
2. Extension should auto-scan
3. Badge: Green ✓
4. Popup: "Safe - No threats detected"
```

**Test with Known Phishing Pattern:**

```
1. Navigate to: http://secure-paypal-login-verify.tk
   (Note: Use a suspicious domain, not real sites)
2. Extension should block
3. Warning page displayed
4. Statistics increment by 1
```

### **4. Test Dashboard (Real Data)**

1. Click "More Data" in popup
2. Dashboard opens in new tab
3. **Verify Real Data:**

   **Hero Metrics:**

   - Attacks Prevented: Should match your blocked count
   - Sites Scanned: Should match your total scans
   - Detection Rate: Should be calculated from real stats
   - Active Users: 1 (your local instance)

   **Charts:**

   - Threats Over Time: Should show activity from your browsing
   - Threat Types: Distribution of your detections
   - NO fake data like "fake-bank-login.com"

   **Recent Activity Feed:**

   - Should show YOUR actual browsing history
   - Real URLs you visited
   - Real timestamps
   - Real risk levels from ML model

### **5. Test Detection History**

1. Click "Detection History" in dashboard sidebar
2. **Expected:**

   ```
   Statistics:
   🚨 Threats Blocked: [your real count]
   ⚠️ Suspicious Sites: [your real count]
   ✅ Safe Sites: [your real count]
   📊 Total Scans: [your real count]
   ```

3. Scroll through timeline
4. **Verify:**
   - All URLs are ones YOU actually visited
   - Timestamps are accurate
   - No fake URLs like "fake-paypal.org"

### **6. Test Data Export**

1. In Detection History, click "📥 Export Data"
2. File downloads: `PhishGuard_RealData_YYYY-MM-DD.json`
3. Open file in text editor
4. **Verify:**

   ```json
   {
     "exportDate": "2024-12-XX...",
     "totalDetections": [your count],
     "statistics": {
       "totalRequests": [your number],
       "blockedRequests": [your number],
       "phishingSitesBlocked": [your number]
     },
     "detections": [
       {
         "timestamp": "[real timestamp]",
         "url": "[URL you visited]",
         "riskLevel": "[actual risk level]",
         "phishingScore": [real score from ML]
       }
     ]
   }
   ```

5. **CRITICAL:** Should contain ZERO fake data:
   - ❌ No "fake-bank-login.com"
   - ❌ No "fake-paypal.org"
   - ❌ No "user1@company.com"
   - ❌ No hardcoded numbers

### **7. Test Settings Persistence**

1. Go to Settings in dashboard
2. Toggle "Real-time Protection" OFF
3. Click "💾 Save Settings"
4. **Expected:** "Settings saved successfully!" notification
5. Close browser completely
6. Reopen browser and extension
7. Go to Settings again
8. **Verify:** "Real-time Protection" is still OFF
9. Toggle back ON and save

### **8. Test Backend Integration**

**Manual API Test:**

```bash
# Test Rust API directly
curl -X POST http://localhost:8080/api/check-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Expected response:
{
  "url": "https://google.com",
  "is_phishing": false,
  "phishing_score": 0.05,
  "risk_level": "safe",
  "features_extracted": true,
  "model_version": "1.0"
}
```

### **9. Test Error Handling**

**Stop Python ML Service:**

```bash
# Find process
ps aux | grep python | grep app.py

# Stop it (or just kill terminal)
```

**Test Extension:**

1. Try to scan a URL
2. **Expected:**
   - Error message: "ML service unavailable"
   - NO demo data fallback
   - Honest error reporting

**Restart Python ML:**

```bash
cd "C:\Users\Sri Vishnu\ml_service"
python app.py
```

**Test Again:**

1. Scan should work normally
2. Extension recovers automatically

---

## 🎯 **Expected Behavior Summary**

| Feature              | Demo Version (OLD)         | Real Version (NEW)          |
| -------------------- | -------------------------- | --------------------------- |
| Popup Statistics     | ❌ Hardcoded: 2847 attacks | ✅ Your actual count        |
| Dashboard Charts     | ❌ Fake data arrays        | ✅ Your browsing aggregated |
| Detection History    | ❌ fake-bank-login.com     | ✅ URLs you visited         |
| Export Data          | ❌ Synthetic JSON          | ✅ Your real data           |
| Settings Persistence | ❌ Broken localStorage     | ✅ chrome.storage.local     |
| Error Handling       | ❌ Shows demo data         | ✅ Shows honest errors      |
| API Endpoint         | ❌ localhost:5000 (wrong)  | ✅ localhost:8080 (correct) |
| Backend Health       | ❌ No checks               | ✅ Every 10s                |
| Update Frequency     | ❌ Static                  | ✅ Real-time (10s)          |

---

## 🐛 **Troubleshooting**

### **Issue: Extension doesn't load**

**Solution:**

```bash
# Check for JavaScript errors
1. chrome://extensions/
2. Click "Errors" on PhishGuard AI
3. Review console output
```

### **Issue: "Backend services offline" error**

**Solution:**

```bash
# Verify services running
netstat -ano | grep "8080\|8000\|6379"

# Should see 3 LISTENING ports
# If missing, start services:

# Redis (Docker)
docker start redis

# Python ML
cd "C:\Users\Sri Vishnu\ml_service"
python app.py

# Rust API
cd "C:\Users\Sri Vishnu\rust_api"
cargo run
```

### **Issue: Popup shows "Loading..." forever**

**Solution:**

1. Open `background.js` in extension
2. Check browser console for errors
3. Verify `ML_API_URL` is `http://localhost:8080/api/check-url`
4. Test API manually with curl (see section 8)

### **Issue: Dashboard shows "No data"**

**Solution:**

```javascript
// Open browser console (F12) in dashboard
// Check chrome storage:
chrome.storage.local.get(["statistics", "recentDetections"], (result) => {
  console.log(result);
});

// Should see your data, not undefined
```

### **Issue: Export downloads empty file**

**Solution:**

- Browse some websites first to generate data
- Wait 10 seconds for sync to storage
- Try export again

---

## ✅ **Success Criteria**

### **All Tests Passing:**

- [x] Extension loads without errors
- [x] Popup displays real statistics (not 2847)
- [x] Dashboard shows your actual browsing history
- [x] Charts update with your data
- [x] Export contains your URLs (no fake data)
- [x] Settings persist across browser restarts
- [x] Backend health checks work
- [x] Error messages are accurate
- [x] Real-time updates every 10s
- [x] No mock/demo/fake data anywhere

### **When Successful, You Should See:**

1. ✅ Your own browsing statistics
2. ✅ URLs you actually visited in history
3. ✅ Charts that change based on your activity
4. ✅ Exported JSON with your real data
5. ✅ Settings that persist
6. ✅ Errors when backend is down (not fake data)

---

## 📊 **Performance Benchmarks**

| Metric            | Target    | How to Verify                 |
| ----------------- | --------- | ----------------------------- |
| API Response Time | < 500ms   | Check network tab in DevTools |
| Statistics Update | Every 10s | Watch popup statistics change |
| Dashboard Load    | < 2s      | Stopwatch dashboard open      |
| Chart Rendering   | < 1s      | Visual inspection             |
| Export Generation | < 1s      | Time from click to download   |
| Memory Usage      | < 100MB   | Chrome Task Manager           |

---

## 🎓 **Understanding the Data Flow**

```
1. User navigates to URL
   ↓
2. background.js detects (webNavigation listener)
   ↓
3. Calls: http://localhost:8080/api/check-url
   ↓
4. Rust API → Python ML → Analyzes 159 features
   ↓
5. Response: { is_phishing: false, phishing_score: 0.05, risk_level: "safe" }
   ↓
6. background.js stores:
   - chrome.storage.local.set({ statistics: { totalRequests: X, blockedRequests: Y } })
   - Adds to recentDetections array
   ↓
7. Every 10 seconds: syncStatisticsToStorage()
   ↓
8. Dashboard reads from chrome.storage.local.get()
   ↓
9. Charts/tables updated with YOUR data
   ↓
10. Export button downloads YOUR data
```

**Key Point:** NO step involves fake/demo/mock data. It's 100% your real browsing.

---

## 🔒 **Security Validation**

### **Test 1: Privacy Check**

```javascript
// Open background.js console
// Inspect API call:
console.log("URL sent to API:", JSON.parse(requestBody));

// Should be the actual URL, not anonymized yet
// (Anonymization happens server-side)
```

### **Test 2: Data Integrity**

```javascript
// Verify storage integrity
chrome.storage.local.get(null, (data) => {
  console.log("All stored data:", data);
  // Should contain:
  // - statistics: { totalRequests, blockedRequests, phishingSitesBlocked }
  // - recentDetections: [array of your scans]
  // - NO fake data
});
```

### **Test 3: Backend Security**

```bash
# Test CORS (should be restricted)
curl -X POST http://localhost:8080/api/check-url \
  -H "Origin: http://evil.com" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Should either succeed (if CORS wide open) or fail (better)
```

---

## 🎉 **Completion Checklist**

Before considering testing complete:

- [ ] Loaded extension in Chrome
- [ ] Clicked extension icon (popup works)
- [ ] Scanned at least 5 different URLs
- [ ] Opened dashboard (shows real data)
- [ ] Viewed Detection History (your URLs, not fake ones)
- [ ] Exported data (contains your actual detections)
- [ ] Changed settings (persisted after browser restart)
- [ ] Stopped backend (extension shows error, not demo data)
- [ ] Restarted backend (extension recovers)
- [ ] Verified no fake URLs in any view

**When all checkboxes are ticked, testing is complete! ✅**

---

**Happy Testing!** 🚀

If you encounter any issues not covered here:

1. Check `FIXES_COMPLETED.md` for architecture details
2. Review browser console for errors
3. Verify all backend services are running
4. Test API endpoints manually with curl

**Remember:** The extension should NEVER show fake data like "fake-bank-login.com" anymore. Everything is real!

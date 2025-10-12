# 🔍 EXTENSION TROUBLESHOOTING GUIDE

## Issue: Extension Logo Removed in Chrome

When Chrome removes the extension logo/icon, it usually means one of these issues:

### ✅ FIXES APPLIED:

1. **Added Icon Files** ✅

   - Created `icon16.svg`
   - Created `icon48.svg`
   - Created `icon128.svg`

2. **Updated manifest.json** ✅
   - Added `"icons"` field
   - Added `"default_icon"` in action

### 🚨 POTENTIAL ISSUES TO CHECK:

#### Issue #1: Manifest V3 webRequest API Deprecated

**Problem**: Chrome Manifest V3 doesn't support blocking in `webRequest.onBeforeRequest`

**Current Code** (extension/background_realtime.js line 426):

```javascript
chrome.webRequest.onBeforeRequest.addListener(
  async function (details) {
    // ...
    return { redirectUrl: chrome.runtime.getURL("warning.html") };
  },
  { urls: ["<all_urls>"] },
  ["blocking"] // ❌ DEPRECATED in Manifest V3
);
```

**Error in Chrome**:

```
Service worker registration failed. Status code: 15
```

**Solution**: Use `declarativeNetRequest` instead of blocking webRequest

---

## 📋 HOW TO CHECK EXTENSION ERRORS IN CHROME:

### Method 1: Extension Management Page

1. Open Chrome: `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Look for your extension
4. Click "Errors" button if it appears
5. Check for red error messages

### Method 2: Service Worker Console

1. Go to `chrome://extensions/`
2. Find "AI Phishing Detector"
3. Click "Service Worker" (if active) or "Errors"
4. See console errors

### Method 3: Background Service Worker Logs

1. `chrome://extensions/`
2. Click "inspect views: service worker"
3. Check Console tab for errors

---

## 🔧 QUICK FIX STEPS:

### Step 1: Check if icons are loaded

1. Go to `chrome://extensions/`
2. Find your extension
3. If no icon appears, icons are missing

### Step 2: Reload Extension

1. Go to `chrome://extensions/`
2. Click the refresh/reload button (circular arrow)
3. Check for error messages

### Step 3: Check Service Worker

1. Look for "Service worker (Inactive)" text
2. If inactive, click it to see errors
3. Common error: "blocking is not supported in Manifest V3"

---

## 🚀 RECOMMENDED FIXES:

### Fix #1: Remove Blocking webRequest (Quick Fix)

Change from blocking to non-blocking:

**Before**:

```javascript
chrome.webRequest.onBeforeRequest.addListener(
  async function (details) {
    return { redirectUrl: ... };
  },
  { urls: ["<all_urls>"] },
  ["blocking"]  // ❌ Remove this
);
```

**After**:

```javascript
chrome.webNavigation.onBeforeNavigate.addListener(
  async function (details) {
    // Check and redirect using chrome.tabs.update
  },
  { url: [{ urlMatches: ".*" }] }
);
```

### Fix #2: Use declarativeNetRequest (Better)

Add to manifest.json:

```json
"permissions": [
  "declarativeNetRequest",
  "declarativeNetRequestWithHostAccess"
],
"declarative_net_request": {
  "rule_resources": [{
    "id": "phishing_rules",
    "enabled": true,
    "path": "rules.json"
  }]
}
```

---

## 📊 CURRENT STATUS:

✅ Icons added
✅ Manifest updated with icons
❓ Service worker may have blocking API issue
❓ Need to check Chrome error console

---

## 🎯 NEXT STEPS:

1. **Reload extension** in Chrome
2. **Check `chrome://extensions/`** for errors
3. **Click "Service Worker"** link to see console
4. **Report the error message** you see
5. I'll fix the specific issue

---

**Created**: October 10, 2025
**Status**: Icons fixed, awaiting error report from Chrome console

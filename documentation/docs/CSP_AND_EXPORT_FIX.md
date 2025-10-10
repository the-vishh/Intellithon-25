# CSP Errors & Export Button Status

## Current Status: ✅ Export Button Should Work

### What's Working:

1. ✅ Export Data button uses `id="exportDataBtn"` (Line 722)
2. ✅ `setupExportDataButton()` function exists (Line 2254)
3. ✅ Event listener is attached in `initializeHistoryPage()` (Line 2039)
4. ✅ CSP in manifest.json allows 'unsafe-inline'
5. ✅ No exportHistory() function in global scope

---

## CSP Errors Explained

The CSP errors you're seeing are from **OTHER buttons** in your dashboard that still use inline `onclick` handlers, NOT from the Export Data button.

### Examples of Other Inline Handlers:

- `onclick="clearHistory()"` (Clear History button)
- `onclick="copyToClipboard()"`
- `onclick="viewDetails()"`
- `onclick="downloadAnalyticsReport()"`
- Many other buttons throughout the app

These CSP errors are **warnings** and don't necessarily break functionality if the CSP allows 'unsafe-inline' (which yours does).

---

## Testing Export Data Button

### Step 1: Reload Extension

```
1. Go to chrome://extensions/
2. Find your extension
3. Click 🔄 Reload
```

### Step 2: Open Dashboard with Console

```
1. Click extension icon
2. Click "Open Dashboard"
3. Press F12 to open Developer Console
```

### Step 3: Navigate to Detection History

```
1. Click "Detection History" in sidebar
2. In console, you should see:
   "✅ Export Data button found, attaching event listener"
```

### Step 4: Click Export Button

```
1. Click "📥 Export Data" button
2. Watch console for these logs:
   🚀 Export Data button clicked!
   📄 JSON data created, size: XXXX bytes
   📦 Blob created
   🔗 Object URL created: blob:...
   📝 Filename: PhishGuard_DetectionHistory_2025-10-09.json
   🖱️ Triggering download...
   🧹 Cleanup complete
3. Alert should appear with success message
4. File should download to Downloads folder
```

---

## If Export Still Doesn't Work

### Debug Steps:

#### 1. Check if button was found:

Open console and look for:

```
✅ Export Data button found, attaching event listener
```

If you see:

```
⚠️ Export button not found
```

Then the button wasn't rendered when the function ran.

#### 2. Manual Test in Console:

Type in browser console:

```javascript
document.getElementById("exportDataBtn");
```

Should return the button element, not `null`.

#### 3. Check if event listener attached:

Type in console:

```javascript
const btn = document.getElementById("exportDataBtn");
console.log(btn.onclick); // Should be null (using addEventListener)
console.log(getEventListeners(btn)); // Should show click listener
```

#### 4. Manually trigger the function:

Type in console:

```javascript
const btn = document.getElementById("exportDataBtn");
if (btn) {
  btn.click();
}
```

---

## Alternative: If Event Listener Doesn't Work

If for some reason the event listener approach still doesn't work, we can use a different approach:

### Option A: Add to window immediately after function definition

```javascript
// Right after setupExportDataButton function
window.setupExportDataButton = setupExportDataButton;
```

### Option B: Use data attribute instead of onclick

```html
<button class="btn-primary" data-action="export">
  <span>📥</span> Export Data
</button>
```

Then use event delegation:

```javascript
document.addEventListener("click", function (e) {
  if (e.target.closest('[data-action="export"]')) {
    // Export logic here
  }
});
```

---

## CSP Errors Solution (Optional)

If you want to eliminate ALL CSP errors, you need to convert ALL inline onclick handlers to event listeners. This is a large refactoring task.

### Example Conversions:

**Before:**

```html
<button onclick="clearHistory()">Clear</button>
```

**After:**

```html
<button id="clearHistoryBtn">Clear</button>
```

```javascript
document
  .getElementById("clearHistoryBtn")
  .addEventListener("click", clearHistory);
```

---

## Current File Status

### app.js (3628 lines):

- Line 722: Export button with `id="exportDataBtn"` ✅
- Line 2039: `setupExportDataButton()` called ✅
- Line 2254-2358: Complete export function ✅
- No inline onclick for export button ✅

### manifest.json:

- CSP includes 'unsafe-inline' ✅
- Downloads permission added ✅

---

## Expected Behavior

When you click "📥 Export Data":

1. Console shows detailed logs
2. JSON file downloads
3. Alert shows success message
4. File contains 8 detection records

**Filename:** `PhishGuard_DetectionHistory_2025-10-09.json`

---

## Troubleshooting Matrix

| Symptom                     | Cause                       | Solution                   |
| --------------------------- | --------------------------- | -------------------------- |
| No console log when clicked | Event listener not attached | Check if button found      |
| "Export button not found"   | Page not loaded             | Add timeout/retry          |
| Download doesn't start      | Blob API issue              | Check browser support      |
| Permission denied           | Browser blocks              | Check download settings    |
| CSP error                   | Other inline handlers       | Convert to event listeners |

---

## Date: October 9, 2025

## Status: Should be working - Test and report back!

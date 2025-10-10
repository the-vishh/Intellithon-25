# Extension Testing Guide

## Current Status

✅ Files Created:

- popup.html, popup.css, popup.js
- dashboard.html, dashboard.css, dashboard.js
- chart.min.js (Chart.js library)
- manifest.json
- README.md

⚠️ Icons: Placeholder icon files created (replace with actual images)

## Testing Steps

### 1. Test the Dashboard Directly

Open `dashboard.html` directly in Chrome:

- Right-click on `dashboard.html` → "Open with" → Chrome
- You should see:
  - Daily Phishing Attempts with mini sparkline chart
  - Top Threat Sources with pie chart
  - Blocked Attacks percentage with shield icon
  - New Attack Variants with warning icon
  - Phishing Trend line chart (blue)
  - Attack Distribution bar chart (green)

### 2. Load as Chrome Extension

1. Open Chrome: `chrome://extensions`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the Extension folder
5. Click the extension icon in toolbar
6. Click "Advanced Controls" → "More Data"

## Troubleshooting

### Charts Not Showing?

**Check Console:**

1. Right-click on dashboard page → Inspect
2. Check Console tab for errors
3. Common issues:
   - Chart.js not loading: Check if chart.min.js exists
   - CSP errors: Check manifest.json content_security_policy

**Verify Chart.js:**

```javascript
// Open console on dashboard and type:
console.log(typeof Chart);
// Should show "function"
```

### Extension Not Loading?

- Check manifest.json is valid JSON
- Icon files must exist (even if empty PNG files)
- Reload extension after any changes

### No Data Showing?

- Currently using mock data
- Check browser console for any fetch errors
- Mock data is in `getMockData()` function in dashboard.js

## Backend Integration

When your backend is ready:

1. **Update API URL** in `dashboard.js`:

```javascript
const API_BASE_URL = "https://your-backend.com/api";
```

2. **Update popup.js** for URL checking:

```javascript
const response = await fetch("https://your-backend.com/api/check-url", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url: currentUrl }),
});
```

## Quick Debug Commands

Open Chrome Console on dashboard page:

```javascript
// Test data fetch
window.dashboardAPI.fetchData().then(console.log);

// Force refresh
window.dashboardAPI.refresh();

// Check if Chart.js loaded
console.log(Chart.version);
```

## File Purposes

- **manifest.json**: Extension configuration
- **popup.html/css/js**: Small popup when clicking extension icon
- **dashboard.html/css/js**: Full dashboard page with charts
- **chart.min.js**: Chart.js library for visualizations

## Next Steps

1. ✅ Test dashboard.html directly in browser
2. ✅ Load as Chrome extension
3. ⏳ Replace placeholder icons with actual logo
4. ⏳ Connect to backend API
5. ⏳ Test with real data

## Common Issues

### Issue: "Uncaught ReferenceError: Chart is not defined"

**Solution:** Chart.js didn't load. Check:

- File path in dashboard.html is correct
- chart.min.js file exists and is not corrupt
- CSP policy allows local scripts

### Issue: Extension icon not showing

**Solution:** Replace placeholder icons with actual PNG images

### Issue: Dashboard opens but charts missing

**Solution:**

1. Open DevTools Console
2. Look for JavaScript errors
3. Verify Chart.js loaded: `console.log(Chart)`
4. Check canvas elements exist in HTML

### Issue: "Failed to fetch"

**Solution:** Normal if backend not set up yet. Uses mock data as fallback.

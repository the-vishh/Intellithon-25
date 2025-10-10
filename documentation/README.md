# AI Phishing Detector Extension

A Chrome extension that detects and tracks phishing websites with an AI-powered backend.

## Features

- **Real-time Protection**: Toggle protection on/off
- **Phishing Counter**: Track the number of phishing sites visited
- **URL Checking**: Send URLs to AI backend for phishing detection
- **Comprehensive Dashboard**: View detailed analytics and trends
- **Modern UI**: Dark theme inspired by Brave browser

## Files Structure

```
Extension/
├── manifest.json          # Extension configuration
├── popup.html            # Extension popup UI
├── popup.css             # Popup styles
├── popup.js              # Popup logic
├── dashboard.html        # Full dashboard page
├── dashboard.css         # Dashboard styles
├── dashboard.js          # Dashboard logic & charts
└── icon*.png            # Extension icons (add your own)
```

## Installation

1. Open Chrome and go to `chrome://extensions`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the Extension folder
5. The extension icon will appear in your toolbar

## Backend Integration

### Dashboard API Endpoint

Update the `API_BASE_URL` in `dashboard.js`:

```javascript
const API_BASE_URL = "http://your-backend-url.com/api";
```

### Expected API Response Format

**GET /api/dashboard**

```json
{
  "dailyAttempts": 1234,
  "blockedPercentage": 89,
  "newVariants": 12,
  "topSource": "Social Media",
  "miniTrend": [20, 35, 30, 45, 50, 55, 48],
  "threatSources": {
    "labels": ["Social Media", "Email", "SMS", "Other"],
    "data": [45, 30, 15, 10],
    "colors": ["#3b82f6", "#10b981", "#06b6d4", "#8b5cf6"]
  },
  "phishingTrend": {
    "labels": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
    "data": [20, 35, 45, 50, 65, 70, 60]
  },
  "attackDistribution": {
    "labels": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    "data": [30, 45, 35, 50, 55, 60, 52, 48, 42, 38]
  }
}
```

### URL Checking API

Update the Send URL functionality in `popup.js`:

```javascript
// Replace the TODO section with:
const response = await fetch("YOUR_BACKEND_API/check-url", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url: currentUrl }),
});
const result = await response.json();

if (result.isPhishing) {
  alert(`⚠️ Warning: This site is identified as phishing!`);
} else {
  alert(`✅ Safe: This site appears to be legitimate.`);
}
```

**POST /check-url**

Request:

```json
{
  "url": "https://example.com"
}
```

Response:

```json
{
  "isPhishing": false,
  "confidence": 0.95,
  "threatLevel": "low",
  "details": "No phishing indicators detected"
}
```

## Dashboard Features

### 1. Daily Phishing Attempts

- Large stat card showing total attempts
- Mini trend chart showing recent activity
- Shield icon indicator

### 2. Top Threat Sources

- Pie chart showing distribution of threat sources
- Displays the top source name

### 3. Blocked Attacks

- Percentage of successfully blocked attacks
- Shield icon indicator

### 4. New Attack Variants

- Count of new phishing variants detected
- Warning triangle icon

### 5. Phishing Trend (Last 7 Days)

- Line chart showing 7-day trend
- Blue gradient area chart

### 6. Attack Distribution by Type

- Bar chart showing attack types
- Green bars for visual consistency

## Auto-Refresh

The dashboard automatically refreshes data every 30 seconds. To manually refresh:

```javascript
window.dashboardAPI.refresh();
```

## Customization

### Colors

Edit `dashboard.css` to change the color scheme:

- Primary gradient: `#1e3a8a` to `#059669`
- Accent colors: Defined in Chart.js configurations

### Chart Types

All charts use Chart.js v4.4.0. Customize in `dashboard.js`:

- Pie Chart: `createThreatPieChart()`
- Line Charts: `createTrendLineChart()`, `createMiniTrendChart()`
- Bar Chart: `createDistributionBarChart()`

## Testing with Mock Data

The dashboard includes mock data for testing. It will automatically use mock data if the backend API is unavailable.

## Next Steps

1. ✅ Add your extension icons (16x16, 32x32, 48x48, 128x128)
2. ✅ Configure your backend API URL
3. ✅ Implement the backend endpoints
4. ✅ Test the extension with real data
5. ✅ Deploy your backend
6. ✅ Publish the extension to Chrome Web Store

## Dependencies

- **Chart.js**: v4.4.0 (loaded via CDN)
- **Chrome Extensions API**: Manifest V3

## Browser Compatibility

- Chrome/Chromium-based browsers
- Manifest V3 compatible

## Support

For issues or questions, please check:

1. Console logs in the extension popup (Right-click > Inspect)
2. Console logs in the dashboard page
3. Network tab for API call failures

---

**Note**: This extension currently uses placeholder data. Connect it to your AI backend to enable full functionality.

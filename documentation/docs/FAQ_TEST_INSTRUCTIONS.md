# FAQ Testing Instructions

## How to Test FAQ Functionality in Help Section

### Step 1: Open the Dashboard

1. Open `index (1).html` in your browser (Chrome recommended)
2. Alternatively, load the extension in Chrome and open the dashboard

### Step 2: Navigate to Help Section

1. Click on the **"Help"** (❓) menu item in the left sidebar
2. Wait for the Help section to load completely

### Step 3: Test FAQ Accordions

1. Scroll down to the **"Frequently Asked Questions"** section
2. You should see 8 FAQ questions with **+** icons
3. Click on any FAQ question

### Expected Behavior:

✅ **When you click a question:**

- The **+** icon should change to **−**
- The answer section should smoothly expand (0.4s animation)
- The answer content should become visible
- Console should show debug messages (press F12 to see)

✅ **When you click another question:**

- The previous FAQ should close automatically
- The new FAQ should open
- Only ONE FAQ should be open at a time

✅ **When you click an open question:**

- The **−** icon should change back to **+**
- The answer should smoothly collapse
- The FAQ should close

### Step 4: Test Category Filters

1. Click on **"Detection"** button - should show only detection FAQs
2. Click on **"Privacy"** button - should show only privacy FAQs
3. Click on **"Technical"** button - should show only technical FAQs
4. Click on **"All"** button - should show all FAQs again

### Step 5: Check Console (F12)

Open Developer Console to see debug messages:

```
toggleFAQ called! <div class="faq-question">
FAQ Item: <div class="faq-item-enhanced">
Answer element: <div class="faq-answer">
Toggle element: <span class="faq-toggle">
Opening FAQ - first closing all others...
Now opening clicked FAQ...
Toggle complete! Active state: true
```

## Troubleshooting

### Problem: FAQs don't expand

**Check:**

- Open Console (F12) - any errors?
- Is `toggleFAQ` being called? (should see console logs)
- Is `style.css` loaded properly?
- Clear browser cache and try again

### Problem: No console logs appear

**Check:**

- Make sure you clicked "Help" in sidebar first
- Verify `app.js` is loaded (check Network tab in DevTools)
- Check for JavaScript errors (Console tab)

### Problem: Animation is jerky

**Check:**

- Verify CSS is loaded (check Elements tab → Computed styles)
- Look for `.faq-item-enhanced.active .faq-answer` style
- Should have `max-height: 1000px` when active

### Problem: Multiple FAQs open at once

**Check:**

- Console should show "closing all others" message
- Verify the forEach loop is executing
- Check if CSS `.active` class is being removed

## Files Involved

- **`index (1).html`** - Main dashboard page
- **`app.js`** - Contains `toggleFAQ()` function (line ~1877)
- **`style.css`** - FAQ styling and animations (line ~2741)

## Quick Test with test-faq.html

If the main dashboard isn't working, test with the standalone file:

1. Open `test-faq.html` in browser
2. Click any FAQ question
3. Should work immediately (no navigation needed)

This isolates whether the issue is with the FAQ code itself or the dashboard integration.

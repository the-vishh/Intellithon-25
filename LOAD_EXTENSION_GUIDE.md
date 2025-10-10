# ✅ LOAD EXTENSION - CORRECT FOLDER

## 🎯 **IMPORTANT: Load the ROOT Folder!**

When you click "Load unpacked" in Chrome, select this folder:

```
c:\Users\Sri Vishnu\Extension
```

**NOT** this folder:

```
c:\Users\Sri Vishnu\Extension\extension  ❌ (Wrong!)
```

---

## 📂 **Correct Folder Structure:**

The ROOT folder (`c:\Users\Sri Vishnu\Extension\`) now contains:

### ✅ Required Files (All Present):

- `manifest.json` ✅ (with icons)
- `popup.html` ✅
- `popup.js` ✅
- `popup.css` ✅
- `app.js` ✅
- `style.css` ✅
- `chart.min.js` ✅
- `dashboard.html` ✅
- `index (1).html` ✅
- `icon16.svg` ✅ (NEW - added)
- `icon48.svg` ✅ (NEW - added)
- `icon128.svg` ✅ (NEW - added)

---

## 🚀 **Step-by-Step Installation:**

### 1. Open Chrome Extensions

Type in address bar:

```
chrome://extensions/
```

### 2. Enable Developer Mode

- Find toggle in **top-right corner**
- Turn it **ON** (should be blue)

### 3. Click "Load unpacked"

- Click the button in top-left

### 4. Navigate to ROOT Folder

In the folder picker, navigate to:

```
C:\Users\Sri Vishnu\Extension
```

**IMPORTANT:** Select the **Extension** folder itself, NOT the **extension** subfolder inside it!

The correct path should show:

```
C:\Users\Sri Vishnu\Extension
```

NOT:

```
C:\Users\Sri Vishnu\Extension\extension  ❌
```

### 5. Click "Select Folder"

### 6. Verify Installation

You should see:

- ✅ Extension name: "Phishing Counter Extension"
- ✅ Blue shield icon 🛡️
- ✅ Version: 1.0
- ✅ No error messages
- ✅ Extension is active (not grayed out)

---

## 🎯 **What's Different from VSCode?**

In VSCode, you see the full folder tree:

```
Extension/
├── extension/        ← Subfolder (contains different version)
├── manifest.json     ← ROOT manifest (this is what Chrome needs!)
├── popup.html
└── ...
```

When loading in Chrome:

- ✅ Select the **Extension** folder (root)
- ❌ DON'T select the **extension** subfolder

---

## ✅ **Verification:**

After loading, check:

1. **Extension appears** with name "Phishing Counter Extension"
2. **Blue shield icon** visible
3. **No errors** in red text
4. **Click extension icon** → popup opens
5. **Click "View Dashboard"** → opens index (1).html

---

## 🔧 **If Issues Occur:**

### Issue: "Manifest file is missing or unreadable"

→ You selected the wrong folder. Select `C:\Users\Sri Vishnu\Extension` (root)

### Issue: "Cannot load extension with file or directory name..."

→ Close the folder picker and select the correct folder again

### Issue: No icon appears

→ The icons are now added! Reload the extension (🔄 button)

---

## 📊 **Comparison:**

| Folder                                     | Purpose                                      | Use For                |
| ------------------------------------------ | -------------------------------------------- | ---------------------- |
| `C:\Users\Sri Vishnu\Extension\`           | **Main extension** (GitHub version)          | ✅ Load this in Chrome |
| `C:\Users\Sri Vishnu\Extension\extension\` | Alternative version with real-time detection | ⚙️ Development/testing |

---

**Action Required:**

1. Go to `chrome://extensions/`
2. Click "Load unpacked"
3. Select: `C:\Users\Sri Vishnu\Extension` (ROOT folder)
4. Done! ✅

---

**Status**: All required files present in ROOT folder, icons added, ready to load!

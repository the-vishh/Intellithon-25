# 🎯 CHROME FOLDER PICKER - HOW TO SELECT CORRECTLY

## ❗ **IMPORTANT: Chrome Shows Only Folders in the Picker!**

This is **NORMAL** behavior. Chrome's "Load unpacked" dialog filters to show **ONLY folders**, not individual files.

---

## 📂 **What You're Seeing:**

### In Chrome's Folder Picker:

```
📁 C:\Users\Sri Vishnu\
  📁 Extension\          ← YOU SEE THIS
    📁 archive\
    📁 backups\
    📁 documentation\
    📁 extension\
    📁 ml-model\
    📁 models\
    ❌ (files hidden by Chrome)
```

### In Windows File Explorer:

```
📁 C:\Users\Sri Vishnu\Extension\
  📄 manifest.json       ✅ You can see this
  📄 popup.html          ✅ You can see this
  📄 app.js              ✅ You can see this
  📄 icon16.svg          ✅ You can see this
  📁 archive\
  📁 backups\
  (etc...)
```

---

## ✅ **SOLUTION: Select the "Extension" Folder Itself**

### Step-by-Step:

1. **Open Chrome**: `chrome://extensions/`

2. **Enable Developer Mode** (top-right toggle)

3. **Click "Load unpacked"**

4. **In the folder picker**, navigate to:

   ```
   C:\Users\Sri Vishnu\
   ```

5. **You'll see**:

   ```
   📁 Extension
   📁 (other folders)
   ```

6. **Click ONCE on "Extension"** to highlight it:

   ```
   📁 Extension  ← Highlighted/selected (blue)
   ```

7. **Click "Select Folder" button** (bottom-right of dialog)
   - **DON'T** double-click to open it
   - **DON'T** look for files inside
   - **JUST** select the folder and click "Select Folder"

---

## 🎯 **Visual Guide:**

### ❌ WRONG: Double-clicking into the folder

```
You navigate: C:\Users\Sri Vishnu\Extension\
You see: archive\, backups\, documentation\, extension\, ml-model\, models\
❌ This is INSIDE the folder - you went too far!
```

### ✅ CORRECT: Selecting the folder itself

```
You navigate: C:\Users\Sri Vishnu\
You see: Extension\, (other folders)
You click: Extension  (highlights it)
You click: "Select Folder" button
✅ Chrome loads the Extension folder!
```

---

## 🔍 **How to Know You're in the Right Place:**

### When you open the folder picker:

1. **Look at the path bar** at the top:

   - ✅ Should show: `C:\Users\Sri Vishnu\`
   - ❌ NOT: `C:\Users\Sri Vishnu\Extension\`

2. **Look at the folder list**:

   - ✅ Should see: `Extension` as a folder you can click
   - ❌ NOT: `archive`, `backups`, `extension` (these are INSIDE)

3. **The "Extension" folder should be selectable** (you can click it once to highlight)

---

## 📋 **Exact Steps (Copy-Paste):**

1. Open: `chrome://extensions/`
2. Toggle: **Developer mode** = ON
3. Click: **"Load unpacked"** button
4. In folder picker address bar, type: `C:\Users\Sri Vishnu\`
5. Press Enter
6. You'll see the **Extension** folder in the list
7. Click **ONCE** on **Extension** to select it (it will highlight)
8. Click the **"Select Folder"** button (bottom-right)
9. Done! ✅

---

## 🎯 **Alternative Method (If Confused):**

1. Open **Windows File Explorer**
2. Navigate to: `C:\Users\Sri Vishnu\Extension\`
3. **Copy the full path** from the address bar:
   ```
   C:\Users\Sri Vishnu\Extension
   ```
4. In Chrome's "Load unpacked" dialog:
   - Paste the path in the address bar
   - Press Enter
   - It will auto-select the folder
5. Click "Select Folder"

---

## 🚨 **Common Mistakes:**

### Mistake #1: Going Inside the Folder

```
❌ You navigate INTO Extension and see subfolders
❌ Path shows: C:\Users\Sri Vishnu\Extension\
```

**Fix**: Go UP one level (click "Sri Vishnu" in the path bar)

### Mistake #2: Selecting a Subfolder

```
❌ You select "extension" subfolder
❌ Chrome loads wrong manifest.json
```

**Fix**: Select "Extension" (capital E), not "extension" (lowercase e)

### Mistake #3: Looking for Files

```
❌ You expect to see manifest.json in the picker
❌ Chrome doesn't show files, only folders
```

**Fix**: This is normal! Just select the folder containing manifest.json

---

## ✅ **Verification:**

After loading, Chrome should show:

- **Extension name**: "Phishing Counter Extension"
- **Version**: 1.0
- **Description**: "Counts the number of phishing websites visited..."
- **Icon**: Blue shield 🛡️
- **Status**: Active (not grayed out)

---

## 🔧 **Still Can't Find It?**

### Try This:

1. Open Windows File Explorer
2. Go to: `C:\Users\Sri Vishnu\Extension\`
3. Verify you see `manifest.json` in that folder
4. Copy the folder path: `C:\Users\Sri Vishnu\Extension`
5. In Chrome's picker, paste that EXACT path
6. Press Enter
7. Click "Select Folder"

---

**TL;DR**:

- Chrome hides files in the picker (shows only folders)
- Navigate to `C:\Users\Sri Vishnu\`
- Select the **Extension** folder (not its contents)
- Click "Select Folder" button
- Done! ✅

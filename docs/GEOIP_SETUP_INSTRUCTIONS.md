# 🌍 GeoIP Setup - Step by Step

## You're on the right page! Here's what to do:

### Step 1: Download the Database

From the page you're on:

1. Find **"GeoLite City"** section
2. Look for:
   - **Edition ID**: `GeoLite2-City`
   - **Format**: `GeoIP2 Binary (.mmdb)`
3. Click **"Download GZIP"** button
4. Save the file (it will be named something like `GeoLite2-City_20251010.tar.gz`)

### Step 2: Extract the File

**Windows (Using 7-Zip or WinRAR)**:

1. Right-click the downloaded `.tar.gz` file
2. Select "Extract Here" or "Extract to GeoLite2-City..."
3. You'll get a folder containing `GeoLite2-City.mmdb`

**OR using Git Bash**:

```bash
cd ~/Downloads
tar -xzf GeoLite2-City_*.tar.gz
```

### Step 3: Move to Project

Create the GeoIP database directory and move the file:

```bash
# Create directory
mkdir -p "C:/Users/Sri Vishnu/Extension/backend/geodb"

# Copy the .mmdb file (adjust the date in filename)
cp ~/Downloads/GeoLite2-City_*/GeoLite2-City.mmdb "C:/Users/Sri Vishnu/Extension/backend/geodb/"
```

**OR manually**:

1. Create folder: `C:\Users\Sri Vishnu\Extension\backend\geodb\`
2. Copy `GeoLite2-City.mmdb` file into that folder

### Step 4: Verify

Check that the file exists:

```bash
ls -lh "C:/Users/Sri Vishnu/Extension/backend/geodb/GeoLite2-City.mmdb"
```

Should show something like:

```
-rw-r--r-- 1 User 197121 70M Oct 10 12:00 GeoLite2-City.mmdb
```

---

## ⚠️ Important Notes

### Don't Download CSV Format

- You want the **Binary (.mmdb)** format
- NOT the CSV format
- The binary format is used by the Rust `maxminddb` library

### File Size

- GeoLite2-City.mmdb is about **70-80 MB**
- If much smaller, something went wrong

### Updates

- Database updated monthly (you saw "Updated: 2025-10-10")
- Consider downloading updates monthly for accuracy

---

## 🔧 After Setup - Enable GeoIP

Once the file is in place, follow `FEATURE_GEOIP.md` to:

1. **Implement the GeoIP service** (`backend/src/services/geoip.rs`)
2. **Update main.rs** to load the database
3. **Modify log_activity()** to capture IP addresses
4. **Update popup** to display country flags
5. **Test** with different IP addresses (use VPN)

---

## 🧪 Quick Test After Implementation

```rust
// In your Rust code
let geoip = GeoIPService::new("geodb/GeoLite2-City.mmdb").unwrap();
let ip: IpAddr = "8.8.8.8".parse().unwrap(); // Google DNS
let country = geoip.lookup_country(ip);
println!("Country: {:?}", country); // Should print USA
```

---

## 🚀 Current Status

- [ ] Download GeoLite2-City (GZIP format)
- [ ] Extract .mmdb file
- [ ] Move to `backend/geodb/` folder
- [ ] Implement GeoIP service (see FEATURE_GEOIP.md)
- [ ] Test with sample IPs

---

## 💡 Quick Command Summary

```bash
# Download from website first, then:

# Navigate to downloads
cd ~/Downloads

# Extract (Windows Git Bash)
tar -xzf GeoLite2-City_*.tar.gz

# Create destination folder
mkdir -p "/c/Users/Sri Vishnu/Extension/backend/geodb"

# Copy the database file
cp GeoLite2-City_*/GeoLite2-City.mmdb "/c/Users/Sri Vishnu/Extension/backend/geodb/"

# Verify
ls -lh "/c/Users/Sri Vishnu/Extension/backend/geodb/GeoLite2-City.mmdb"
```

---

**Next Step**: Click "Download GZIP" on the MaxMind page! 📥

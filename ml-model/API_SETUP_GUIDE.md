# 🔑 API CONFIGURATION GUIDE

## Setting Up Threat Intelligence APIs

All threat intelligence APIs are **FREE** to use! Here's how to get your keys:

---

## 1. PhishTank API (FREE) ✅

**What it does:** Access to 50,000+ confirmed phishing URLs

**How to get API key:**

1. Go to: https://www.phishtank.com/api_info.php
2. Click "Register for an API Key"
3. Fill in your email and details
4. Verify your email
5. Copy your API key

**Set it up:**

```bash
# Windows (PowerShell)
$env:PHISHTANK_API_KEY="your_key_here"

# Linux/Mac
export PHISHTANK_API_KEY="your_key_here"

# Or create .env file:
echo 'PHISHTANK_API_KEY=your_key_here' >> .env
```

**Features:**

- ✅ 50,000+ confirmed phishing sites
- ✅ Community-verified submissions
- ✅ Free tier: 500 queries/hour
- ✅ No credit card required

---

## 2. Google Safe Browsing API (FREE) ✅

**⚠️ IMPORTANT: Use Safe Browsing API v4 (NOT Legacy)**

**What it does:** Google's database of 1M+ malicious URLs

**How to get API key:**

1. Go to: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. **Enable "Safe Browsing API"** (v4 - the CURRENT version)
   - ❌ **DO NOT** use "Safe Browsing API (Legacy)" - it's deprecated!
   - ✅ **USE** "Safe Browsing API" - this is v4, the active version
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

**API Version Details:**

- ✅ **Safe Browsing API (v4):** Current, actively maintained, use this!
- ❌ **Safe Browsing API (Legacy):** Old, deprecated, don't use

**Set it up:**

```bash
# Windows (PowerShell)
$env:GOOGLE_SAFE_BROWSING_KEY="your_key_here"

# Linux/Mac
export GOOGLE_SAFE_BROWSING_KEY="your_key_here"

# Or in .env file:
echo 'GOOGLE_SAFE_BROWSING_KEY=your_key_here' >> .env
```

**Features:**

- ✅ 1,000,000+ malicious URLs
- ✅ Updated continuously
- ✅ Free tier: 10,000 queries/day
- ✅ No credit card required

---

## 3. VirusTotal API (FREE) ✅

**What it does:** 70+ antivirus engines scanning URLs/files

**How to get API key:**

1. Go to: https://www.virustotal.com/
2. Sign up for a free account
3. Go to your profile → API Key
4. Copy your API key

**Set it up:**

```bash
# Windows (PowerShell)
$env:VIRUSTOTAL_API_KEY="your_key_here"

# Linux/Mac
export VIRUSTOTAL_API_KEY="your_key_here"

# Or in .env file:
echo 'VIRUSTOTAL_API_KEY=your_key_here' >> .env
```

**Features:**

- ✅ 70+ antivirus engines
- ✅ URL and file scanning
- ✅ Free tier: 4 requests/minute
- ✅ No credit card required

---

## 🚀 QUICK SETUP (All 3 APIs at once)

### Option 1: Environment Variables (Temporary)

**Windows PowerShell:**

```powershell
$env:PHISHTANK_API_KEY="paste_your_phishtank_key"
$env:GOOGLE_SAFE_BROWSING_KEY="paste_your_google_key"
$env:VIRUSTOTAL_API_KEY="paste_your_virustotal_key"
```

**Linux/Mac Terminal:**

```bash
export PHISHTANK_API_KEY="paste_your_phishtank_key"
export GOOGLE_SAFE_BROWSING_KEY="paste_your_google_key"
export VIRUSTOTAL_API_KEY="paste_your_virustotal_key"
```

### Option 2: .env File (Permanent)

Create file `ml-model/.env`:

```bash
PHISHTANK_API_KEY=your_phishtank_key_here
GOOGLE_SAFE_BROWSING_KEY=your_google_safe_browsing_key_here
VIRUSTOTAL_API_KEY=your_virustotal_key_here
```

Then install python-dotenv:

```bash
pip install python-dotenv
```

And load in code:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## ✅ VERIFY YOUR SETUP

Run this test script:

```bash
cd ml-model
python3 utils/threat_intelligence.py
```

You should see:

```
🔑 API KEY STATUS:
   PhishTank: ✅ Configured
   Google Safe Browsing: ✅ Configured
   VirusTotal: ✅ Configured
```

---

## 📊 API LIMITS (Free Tiers)

| API                  | Free Limit | Enough For                   |
| -------------------- | ---------- | ---------------------------- |
| PhishTank            | 500/hour   | ✅ Personal use              |
| Google Safe Browsing | 10,000/day | ✅ Personal + small business |
| VirusTotal           | 4/minute   | ✅ Personal use              |

**Combined:** More than enough for personal browsing protection!

---

## 🔒 SECURITY BEST PRACTICES

1. **Never commit API keys to Git:**

   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use separate keys for dev/prod**

3. **Rotate keys every 90 days**

4. **Monitor your usage:**
   - PhishTank: https://www.phishtank.com/api_info.php
   - Google: https://console.cloud.google.com/apis/dashboard
   - VirusTotal: https://www.virustotal.com/gui/user/YOUR_USERNAME/apikey

---

## 🆓 ALL FREE - NO CREDIT CARD NEEDED!

All three APIs are **completely free** for personal use. No credit card required!

**Total Setup Time:** ~15 minutes
**Cost:** $0.00
**Protection Level:** Enterprise-grade 🛡️

---

## 🧪 TEST WITH REAL PHISHING SITES

Once configured, test with these known phishing sites:

```python
from utils.threat_intelligence import ThreatIntelligence

threat_intel = ThreatIntelligence()

# Test with known phishing site
report = threat_intel.check_url("http://data-paypal-login.tk/verify")

print(f"Is Threat: {report['is_threat']}")
print(f"Threat Score: {report['threat_score']}")
print(f"Sources: {report['sources']}")
```

---

## 💡 PRO TIPS

1. **Rate Limiting:** The code automatically handles rate limits with caching

2. **Fallback:** Works without API keys (reduced accuracy)

3. **Caching:** Results cached for 1 hour to save API calls

4. **Batch Checking:** Can check multiple URLs efficiently

---

## 🚀 READY TO USE!

Once you have your API keys, the threat intelligence system will automatically:

- ✅ Check URLs against all 3 sources
- ✅ Cache results for speed
- ✅ Handle API failures gracefully
- ✅ Aggregate threat scores
- ✅ Provide detailed reports

**Your phishing detector just became ENTERPRISE-GRADE!** 🛡️

---

For support: Check the API documentation links above

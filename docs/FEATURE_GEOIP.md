# 🌍 GeoIP Integration Guide

## Overview

Add geographic threat source tracking using MaxMind GeoIP2 database.

## Step 1: Download GeoIP Database

### Option A: Free GeoLite2 (Recommended for testing)

1. Register at https://www.maxmind.com/en/geolite2/signup
2. Download `GeoLite2-City.mmdb` or `GeoLite2-Country.mmdb`
3. Place in `backend/geodb/` directory

### Option B: Commercial GeoIP2 (Production)

1. Purchase GeoIP2 from MaxMind
2. Download database
3. Place in `backend/geodb/`

## Step 2: Backend Implementation

Already added in `backend/Cargo.toml`:

```toml
maxminddb = "0.24"
```

### Create GeoIP Service

File: `backend/src/services/geoip.rs`

```rust
use maxminddb::{geoip2, MaxMindDBError, Reader};
use std::net::IpAddr;
use std::sync::Arc;

pub struct GeoIPService {
    reader: Arc<Reader<Vec<u8>>>,
}

impl GeoIPService {
    pub fn new(db_path: &str) -> Result<Self, MaxMindDBError> {
        let reader = maxminddb::Reader::open_readfile(db_path)?;
        Ok(Self {
            reader: Arc::new(reader),
        })
    }

    pub fn lookup_country(&self, ip: IpAddr) -> Option<CountryInfo> {
        let country: geoip2::Country = self.reader.lookup(ip).ok()?;

        Some(CountryInfo {
            code: country.country?.iso_code?.to_string(),
            name: country.country?.names?.get("en")?.to_string(),
        })
    }

    pub fn lookup_city(&self, ip: IpAddr) -> Option<CityInfo> {
        let city: geoip2::City = self.reader.lookup(ip).ok()?;

        Some(CityInfo {
            country_code: city.country?.iso_code?.to_string(),
            country_name: city.country?.names?.get("en")?.to_string(),
            city_name: city.city?.names?.get("en")?.to_string(),
            latitude: city.location?.latitude?,
            longitude: city.location?.longitude?,
        })
    }
}

#[derive(Debug, Clone)]
pub struct CountryInfo {
    pub code: String,
    pub name: String,
}

#[derive(Debug, Clone)]
pub struct CityInfo {
    pub country_code: String,
    pub country_name: String,
    pub city_name: String,
    pub latitude: f64,
    pub longitude: f64,
}
```

### Update Main App State

File: `backend/src/main.rs`

```rust
mod services;
use services::geoip::GeoIPService;

pub struct AppState {
    db_pool: DbPool,
    redis_pool: RedisPool,
    ml_api_url: String,
    geoip: Arc<GeoIPService>,  // NEW
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // ... existing code ...

    // Initialize GeoIP
    let geoip = Arc::new(
        GeoIPService::new("geodb/GeoLite2-City.mmdb")
            .expect("Failed to load GeoIP database")
    );

    let app_state = web::Data::new(AppState {
        db_pool: pool.clone(),
        redis_pool: redis_pool.clone(),
        ml_api_url: ml_api_url.clone(),
        geoip,  // NEW
    });

    // ... rest of code ...
}
```

### Use in Activity Logging

File: `backend/src/handlers/user_analytics.rs`

```rust
pub async fn log_activity(
    pool: web::Data<DbPool>,
    app_state: web::Data<AppState>,  // NEW
    user_id_path: web::Path<Uuid>,
    request: web::Json<LogActivityRequest>,
) -> ActixResult<HttpResponse> {
    let user_id = *user_id_path;
    let req = request.into_inner();

    // Extract IP from request (if available)
    let client_ip = req.client_ip.and_then(|ip_str| ip_str.parse().ok());

    let result = web::block(move || {
        let mut conn = pool.get()?;

        // Insert activity
        let new_activity = NewUserActivity { /* ... */ };
        let activity = diesel::insert_into(user_activity::table)
            .values(&new_activity)
            .get_result::<UserActivity>(&mut conn)?;

        // Lookup geographic info if IP available
        if let Some(ip) = client_ip {
            if let Some(country) = app_state.geoip.lookup_country(ip) {
                // Check if country already exists
                let existing = user_threat_sources::table
                    .filter(user_threat_sources::user_id.eq(user_id))
                    .filter(user_threat_sources::country_code.eq(&country.code))
                    .first::<UserThreatSource>(&mut conn)
                    .optional()?;

                if let Some(mut source) = existing {
                    // Update count
                    source.threat_count += 1;
                    diesel::update(user_threat_sources::table)
                        .filter(user_threat_sources::source_id.eq(source.source_id))
                        .set((
                            user_threat_sources::threat_count.eq(source.threat_count),
                            user_threat_sources::last_seen.eq(Utc::now()),
                        ))
                        .execute(&mut conn)?;
                } else {
                    // Insert new country
                    let new_source = NewUserThreatSource {
                        user_id,
                        country_code: Some(country.code),
                        country_name: Some(country.name),
                        threat_count: 1,
                    };
                    diesel::insert_into(user_threat_sources::table)
                        .values(&new_source)
                        .execute(&mut conn)?;
                }
            }
        }

        Ok::<_, diesel::result::Error>(activity.activity_id)
    }).await?;

    // ... rest of code ...
}
```

### Update Request Model

```rust
#[derive(Debug, Deserialize)]
pub struct LogActivityRequest {
    pub encrypted_url: String,
    pub encrypted_url_hash: String,
    pub domain: String,
    pub is_phishing: bool,
    pub threat_type: Option<String>,
    pub threat_level: Option<String>,
    pub confidence: f64,
    pub action_taken: String,
    pub client_ip: Option<String>,  // NEW
}
```

## Step 3: Extension Updates

### Update background.js to send IP

File: `background.js`

```javascript
async function logUserActivity(url, scanResult) {
  try {
    const userId = await getUserId();
    const key = await deriveEncryptionKey(userId);
    const encrypted = await encryptURL(url, key);
    const urlHash = await hashForIndexing(url);
    const domain = extractDomain(url);

    // Get client IP (optional - privacy consideration!)
    let clientIp = null;
    try {
      const ipResponse = await fetch("https://api.ipify.org?format=json");
      const ipData = await ipResponse.json();
      clientIp = ipData.ip;
    } catch (e) {
      console.log("Could not fetch IP:", e);
    }

    const activity = {
      encrypted_url: encrypted.ciphertext,
      encrypted_url_hash: urlHash,
      domain: domain || "unknown",
      is_phishing: scanResult.is_phishing || false,
      threat_type: scanResult.threat_type || null,
      threat_level: scanResult.threat_level || null,
      confidence: scanResult.confidence || 0.0,
      action_taken: scanResult.blocked ? "blocked" : "allowed",
      client_ip: clientIp, // NEW
    };

    await fetch(`${CONFIG.ANALYTICS_API_URL}/${userId}/activity`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(activity),
    });
  } catch (error) {
    console.error("Failed to log activity:", error);
  }
}
```

### Update Popup to Show Geographic Sources

File: `popup-enhanced.js`

```javascript
function updateThreatSources(sources) {
  const container = document.getElementById("threat-sources");

  if (!sources || sources.length === 0) {
    container.innerHTML =
      '<div class="no-data">No threat sources detected</div>';
    return;
  }

  container.innerHTML = sources
    .slice(0, 5)
    .map(
      (source) => `
    <div class="source-item">
      <span class="source-flag">${getCountryFlag(source.country_code)}</span>
      <div class="source-info">
        <div class="source-country">${source.country_name}</div>
        <div class="source-count">${source.threat_count} threats</div>
      </div>
      <div class="source-bar">
        <div class="source-bar-fill" style="width: ${
          (source.threat_count / sources[0].threat_count) * 100
        }%"></div>
      </div>
    </div>
  `
    )
    .join("");
}

function getCountryFlag(countryCode) {
  if (!countryCode || countryCode.length !== 2) return "🌍";
  const codePoints = countryCode
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt());
  return String.fromCodePoint(...codePoints);
}
```

## Step 4: Testing

1. **Download GeoIP database** and place in `backend/geodb/`
2. **Restart Rust API** with GeoIP loaded
3. **Visit websites** from different regions (use VPN to test)
4. **Check popup** - should show geographic threat sources with flags
5. **Verify database**:

```sql
SELECT country_code, country_name, threat_count
FROM user_threat_sources
ORDER BY threat_count DESC;
```

## Privacy Considerations

⚠️ **Important**: Collecting IP addresses has privacy implications!

Options:

1. **Don't collect IPs** - Extract from server logs only
2. **Make it opt-in** - Let users enable/disable
3. **Anonymize immediately** - Hash IP before storing
4. **Respect Do Not Track** - Check browser setting

## Troubleshooting

### Database not loading

```
Error: Failed to load GeoIP database
```

**Fix**: Check file path and permissions

### IP not resolving

```
Warning: Could not lookup country for IP
```

**Fix**: Ensure IP is public (not 127.0.0.1 or private range)

### Missing country data

```
Country code: null
```

**Fix**: IP might be from unknown/private range, or database needs update

---

**Status**: 🔧 Manual implementation required
**Complexity**: Medium
**Time**: 30-45 minutes

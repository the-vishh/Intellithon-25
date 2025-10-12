/*!
 * 🌍 GeoIP Lookup Service
 * Using MaxMind GeoLite2-City database
 */

use maxminddb::{geoip2, MaxMindDBError, Reader};
use std::net::IpAddr;
use std::sync::Arc;

/// GeoIP lookup service for threat source tracking
pub struct GeoIPService {
    reader: Arc<Reader<Vec<u8>>>,
}

impl GeoIPService {
    /// Create new GeoIP service with database file
    pub fn new(db_path: &str) -> Result<Self, MaxMindDBError> {
        let reader = maxminddb::Reader::open_readfile(db_path)?;
        Ok(Self {
            reader: Arc::new(reader),
        })
    }

    /// Lookup country information from IP address
    pub fn lookup_country(&self, ip: IpAddr) -> Option<CountryInfo> {
        let country: geoip2::Country = self.reader.lookup(ip).ok()?;

        let country_record = country.country?;
        let iso_code = country_record.iso_code?.to_string();
        let name = country_record.names?
            .get("en")
            .map(|s| s.to_string())
            .unwrap_or_else(|| iso_code.clone());

        Some(CountryInfo {
            code: iso_code,
            name,
        })
    }

    /// Lookup detailed city information from IP address
    pub fn lookup_city(&self, ip: IpAddr) -> Option<CityInfo> {
        let city: geoip2::City = self.reader.lookup(ip).ok()?;

        let country_record = city.country?;
        let country_code = country_record.iso_code?.to_string();
        let country_name = country_record.names?
            .get("en")
            .map(|s| s.to_string())
            .unwrap_or_else(|| country_code.clone());

        let city_record = city.city;
        let city_name = city_record
            .and_then(|c| c.names)
            .and_then(|names| names.get("en").map(|s| s.to_string()))
            .unwrap_or_else(|| "Unknown".to_string());

        let location = city.location?;
        let latitude = location.latitude?;
        let longitude = location.longitude?;

        Some(CityInfo {
            country_code,
            country_name,
            city_name,
            latitude,
            longitude,
        })
    }
}

/// Basic country information
#[derive(Debug, Clone)]
pub struct CountryInfo {
    pub code: String,
    pub name: String,
}

/// Detailed city and location information
#[derive(Debug, Clone)]
pub struct CityInfo {
    pub country_code: String,
    pub country_name: String,
    pub city_name: String,
    pub latitude: f64,
    pub longitude: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_google_dns() {
        // Test with Google's public DNS (should be USA)
        let geoip = GeoIPService::new("geodb/GeoLite2-City.mmdb");
        if let Ok(service) = geoip {
            let ip: IpAddr = "8.8.8.8".parse().unwrap();
            let country = service.lookup_country(ip);
            assert!(country.is_some());
            if let Some(c) = country {
                assert_eq!(c.code, "US");
            }
        }
    }
}

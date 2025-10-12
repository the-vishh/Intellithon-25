/*!
 * Redis caching service
 */

use redis::{Client, AsyncCommands};
use redis::aio::ConnectionManager;
use sha2::{Sha256, Digest};
use anyhow::Result;

use crate::models::URLCheckResponse;

/// Redis cache service for storing URL check results
#[derive(Clone)]
pub struct CacheService {
    client: ConnectionManager,
}

impl CacheService {
    /// Create new cache service
    pub async fn new(redis_url: &str) -> Result<Self> {
        let client = Client::open(redis_url)?;
        let manager = ConnectionManager::new(client).await?;

        Ok(Self {
            client: manager,
        })
    }

    /// Generate cache key from URL
    fn cache_key(url: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(url.as_bytes());
        let hash = hasher.finalize();
        format!("phishing:v1:{}", hex::encode(hash))
    }

    /// Get cached result for URL
    pub async fn get(&mut self, url: &str) -> Result<Option<URLCheckResponse>> {
        let key = Self::cache_key(url);

        let result: Option<String> = self.client.get(&key).await?;

        match result {
            Some(json) => {
                let response: URLCheckResponse = serde_json::from_str(&json)?;
                log::debug!("✅ Cache HIT for URL: {}", url);
                Ok(Some(response))
            }
            None => {
                log::debug!("❌ Cache MISS for URL: {}", url);
                Ok(None)
            }
        }
    }

    /// Store result in cache
    pub async fn set(&mut self, url: &str, response: &URLCheckResponse, ttl_seconds: usize) -> Result<()> {
        let key = Self::cache_key(url);
        let json = serde_json::to_string(response)?;

        let _: () = self.client.set_ex(&key, json, ttl_seconds as u64).await?;

        log::debug!("💾 Cached result for URL: {} (TTL: {}s)", url, ttl_seconds);
        Ok(())
    }

    /// Check if Redis is healthy
    pub async fn health_check(&mut self) -> Result<bool> {
        // Try a simple GET operation instead of PING
        let _: Option<String> = self.client.get("__health_check__").await?;
        Ok(true)
    }

    /// Get cache statistics
    pub async fn get_stats(&mut self) -> Result<(usize, usize)> {
        // Redis INFO command requires using redis::cmd
        // For now, return default values
        Ok((0, 0))
    }
}

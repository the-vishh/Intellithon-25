/*!
 * Request/Response models
 */

use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

/// Request to check if a URL is phishing
#[derive(Debug, Deserialize, Serialize)]
pub struct URLCheckRequest {
    pub url: String,
    #[serde(default = "default_sensitivity_mode")]
    pub sensitivity_mode: String,
}

fn default_sensitivity_mode() -> String {
    "balanced".to_string()
}

/// Response with phishing detection results
#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct URLCheckResponse {
    pub url: String,
    pub is_phishing: bool,
    pub confidence: f64,
    pub threat_level: String,
    pub sensitivity_mode: String,
    pub threshold_used: f64,
    pub details: serde_json::Value,
    pub latency_ms: f64,
    pub cached: bool,
    pub timestamp: DateTime<Utc>,
    pub performance_metrics: serde_json::Value,
    pub model_version: String,
}

/// Health check response
#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub redis: String,
    pub ml_service: String,
    pub timestamp: DateTime<Utc>,
}

/// Statistics response
#[derive(Debug, Serialize)]
pub struct StatsResponse {
    pub total_requests: u64,
    pub cache_hits: u64,
    pub cache_misses: u64,
    pub cache_hit_rate: f64,
    pub average_latency_ms: f64,
}

/// Error response
#[derive(Debug, Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub message: String,
    pub timestamp: DateTime<Utc>,
}

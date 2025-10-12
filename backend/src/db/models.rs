// NOTE: Converted for SQLite - UUID types are now String, DateTime types are i64 (Unix timestamps)

/*!
 * Database models using Diesel ORM
 */

use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::schema::users;

// ============================================================================
// USER MODEL
// ============================================================================

#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize)]
#[diesel(table_name = users)]
#[diesel(primary_key(user_id))]
pub struct User {
    pub user_id: String,
    pub extension_id: String,
    pub email: Option<String>,
    pub username: Option<String>,
    pub sensitivity_mode: String,
    pub protection_enabled: i32,
    pub ai_detection_enabled: i32,
    pub subscription_tier: String,
    pub subscription_expires_at: Option<i64>,
    pub created_at: i64,
    pub last_active_at: i64,
    pub total_scans: i32,
    pub total_threats_blocked: i32,
    pub average_response_time_ms: f64,
    pub is_active: i32,
    pub is_banned: i32,
    pub ban_reason: Option<String>,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = users)]
pub struct NewUser {
    pub user_id: String,
    pub extension_id: String,
    pub email: Option<String>,
    pub username: Option<String>,
    pub sensitivity_mode: String,
}

// ============================================================================
// SCAN MODEL - Using user_activity table instead
// ============================================================================

// Commented out - we use user_activity table for scan logs
/*
#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize, Associations)]
#[diesel(table_name = scans)]
#[diesel(primary_key(scan_id))]
#[diesel(belongs_to(User, foreign_key = user_id))]
pub struct Scan {
    pub scan_id: String,
    pub user_id: String,
    pub url: String,
    pub url_hash: String,
    pub domain: Option<String>,
    pub is_phishing: i32,
    pub confidence: f64,
    pub threat_level: String,
    pub sensitivity_mode: String,
    pub threshold_used: f64,
    pub model_version: String,
    pub latency_ms: f64,
    pub feature_extraction_ms: Option<f64>,
    pub ml_inference_ms: Option<f64>,
    pub details: Option<serde_json::Value>,
    pub blocked: i32,
    pub user_feedback: Option<String>,
    pub scanned_at: i64,
    pub ip_address: Option<String>,
    pub user_agent: Option<String>,
    pub cached: i32,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = scans)]
pub struct NewScan {
    pub scan_id: String,
    pub user_id: String,
    pub url: String,
    pub url_hash: String,
    pub domain: Option<String>,
    pub is_phishing: i32,
    pub confidence: f64,
    pub threat_level: String,
    pub sensitivity_mode: String,
    pub threshold_used: f64,
    pub model_version: String,
    pub latency_ms: f64,
    pub feature_extraction_ms: Option<f64>,
    pub ml_inference_ms: Option<f64>,
    pub details: Option<serde_json::Value>,
    pub blocked: i32,
    pub cached: i32,
}
*/

// ============================================================================
// MODEL METRICS MODEL - Using device_metrics table instead
// ============================================================================

// Commented out - we use device_metrics table for performance tracking
/*
#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize)]
#[diesel(table_name = model_metrics)]
#[diesel(primary_key(metric_id))]
pub struct ModelMetrics {
    pub metric_id: String,
    pub model_version: String,
    pub period_start: i64,
    pub period_end: i64,
    pub total_predictions: i32,
    pub total_phishing_detected: i32,
    pub total_safe_detected: i32,
    pub true_positives: i32,
    pub true_negatives: i32,
    pub false_positives: i32,
    pub false_negatives: i32,
    pub average_latency_ms: Option<f64>,
    pub p95_latency_ms: Option<f64>,
    pub p99_latency_ms: Option<f64>,
    pub conservative_scans: i32,
    pub balanced_scans: i32,
    pub aggressive_scans: i32,
    pub calculated_at: i64,
}
*/

// ============================================================================
// GLOBAL STATS MODEL - Using user_threat_stats aggregation instead
// ============================================================================

// Commented out - we aggregate from user_threat_stats table
/*
#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize)]
#[diesel(table_name = global_stats)]
#[diesel(primary_key(stat_id))]
pub struct GlobalStats {
    pub stat_id: String,
    pub stat_period: String,
    pub period_start: i64,
    pub period_end: Option<i64>,
    pub total_users: i32,
    pub active_users: i32,
    pub new_users: i32,
    pub total_scans: i32,
    pub phishing_detected: i32,
    pub safe_urls: i32,
    pub critical_threats: i32,
    pub high_threats: i32,
    pub medium_threats: i32,
    pub low_threats: i32,
    pub conservative_mode_usage: i32,
    pub balanced_mode_usage: i32,
    pub aggressive_mode_usage: i32,
    pub average_latency_ms: Option<f64>,
    pub average_confidence: Option<f64>,
    pub top_phishing_domains: Option<serde_json::Value>,
    pub top_safe_domains: Option<serde_json::Value>,
    pub geographic_distribution: Option<serde_json::Value>,
    pub current_accuracy: Option<f64>,
    pub current_precision: Option<f64>,
    pub current_recall: Option<f64>,
    pub calculated_at: i64,
}
*/

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

// Commented out - NewScan struct is commented out above
/*
impl NewScan {
    /// Create NewScan from URLCheckResponse
    pub fn from_response(
        user_id: String,
        url: &str,
        response: &crate::models::URLCheckResponse,
    ) -> Self {
        use sha2::{Sha256, Digest};

        let mut hasher = Sha256::new();
        hasher.update(url.as_bytes());
        let url_hash = format!("{:x}", hasher.finalize());

        let domain = url
            .split("://")
            .nth(1)
            .and_then(|s| s.split('/').next())
            .map(String::from);

        Self {
            scan_id: Uuid::new_v4().to_string(),
            user_id: user_id.to_string(),
            url: url.to_string(),
            url_hash,
            domain,
            is_phishing: if response.is_phishing { 1 } else { 0 },
            confidence: response.confidence,
            threat_level: response.threat_level.clone(),
            sensitivity_mode: response.sensitivity_mode.clone(),
            threshold_used: response.threshold_used,
            model_version: response.model_version.clone(),
            latency_ms: response.latency_ms,
            feature_extraction_ms: response.performance_metrics
                .get("feature_extraction_ms")
                .and_then(|v| v.as_f64()),
            ml_inference_ms: response.performance_metrics
                .get("ml_inference_ms")
                .and_then(|v| v.as_f64()),
            details: Some(serde_json::to_value(&response.details).unwrap_or(serde_json::Value::Null)),
            blocked: if response.is_phishing { 1 } else { 0 },
            cached: if response.cached { 1 } else { 0 },
        }
    }
}
*/

impl NewUser {
    /// Create new user with default settings
    pub fn new(extension_id: String) -> Self {
        Self {
            user_id: Uuid::new_v4().to_string(),
            extension_id,
            email: None,
            username: None,
            sensitivity_mode: "balanced".to_string(),
        }
    }
}

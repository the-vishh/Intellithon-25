// NOTE: Converted for SQLite - UUID types are now String, DateTime types are i64 (Unix timestamps)

// 📊 USER ANALYTICS DATABASE MODELS
// Diesel models for personal analytics tables

use diesel::prelude::*;
use serde::{Deserialize, Serialize};

use crate::db::schema_analytics::*;
use crate::db::models::User;

// ==========================================
// USER ACTIVITY (Real-Time Feed)
// ==========================================

#[derive(Debug, Queryable, Selectable, Identifiable, Associations, Serialize, Deserialize)]
#[diesel(table_name = user_activity)]
#[diesel(belongs_to(User, foreign_key = user_id))]
#[diesel(primary_key(activity_id))]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct UserActivity {
    pub activity_id: String,
    pub user_id: String,
    pub encrypted_url: String,
    pub url_hash: String,
    pub encrypted_domain: String,
    pub domain_hash: String,
    pub is_phishing: i32,
    pub threat_type: Option<String>,
    pub threat_level: String,
    pub confidence: Option<f64>,
    pub action_taken: String,
    pub user_override: i32,
    pub encryption_nonce: String,
    pub timestamp: i64,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = user_activity)]
pub struct NewUserActivity {
    pub user_id: String,
    pub encrypted_url: String,
    pub url_hash: String,
    pub encrypted_domain: String,
    pub domain_hash: String,
    pub is_phishing: i32,
    pub threat_type: Option<String>,
    pub threat_level: String,
    pub confidence: Option<f64>,
    pub action_taken: String,
    pub encryption_nonce: String,
}

// ==========================================
// DEVICE METRICS (Performance Tracking)
// ==========================================

#[derive(Debug, Queryable, Identifiable, Associations, Serialize, Deserialize)]
#[diesel(table_name = device_metrics)]
#[diesel(belongs_to(User, foreign_key = user_id))]
#[diesel(primary_key(metric_id))]
pub struct DeviceMetrics {
    pub metric_id: String,
    pub user_id: String,
    pub device_fingerprint: String,
    pub browser: Option<String>,
    pub browser_version: Option<String>,
    pub os: Option<String>,
    pub extension_version: Option<String>,
    pub avg_processing_speed_ms: Option<f64>,
    pub memory_usage_mb: Option<f64>,
    pub cache_hit_rate: Option<f64>,
    pub feature_extraction_ms: Option<f64>,
    pub ml_inference_ms: Option<f64>,
    pub network_latency_ms: Option<f64>,
    pub local_db_size_mb: Option<f64>,
    pub cache_entries: Option<i32>,
    pub last_cache_clear: Option<i64>,
    pub pending_scans: Option<i32>,
    pub failed_scans: Option<i32>,
    pub model_version: Option<String>,
    pub model_last_updated: Option<i64>,
    pub model_size_mb: Option<f64>,
    pub first_seen: i64,
    pub last_updated: i64,
}

#[derive(Debug, Insertable, AsChangeset)]
#[diesel(table_name = device_metrics)]
pub struct NewDeviceMetrics {
    pub user_id: String,
    pub device_fingerprint: String,
    pub browser: Option<String>,
    pub browser_version: Option<String>,
    pub os: Option<String>,
    pub extension_version: Option<String>,
    pub avg_processing_speed_ms: Option<f64>,
    pub model_version: Option<String>,
}

// ==========================================
// USER THREAT STATS (Breakdown)
// ==========================================

#[derive(Debug, Queryable, Selectable, Identifiable, Associations, Serialize, Deserialize)]
#[diesel(table_name = user_threat_stats)]
#[diesel(belongs_to(User, foreign_key = user_id))]
#[diesel(primary_key(stat_id))]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct UserThreatStats {
    pub stat_id: String,
    pub user_id: String,
    pub phishing_count: i32,
    pub malware_count: i32,
    pub cryptojacking_count: i32,
    pub ransomware_count: i32,
    pub scam_count: i32,
    pub data_harvesting_count: i32,
    pub critical_threats: i32,
    pub high_threats: i32,
    pub medium_threats: i32,
    pub low_threats: i32,
    pub total_blocked: i32,
    pub total_warnings: i32,
    pub total_allowed: i32,
    pub period_start: Option<i64>,
    pub period_end: Option<i64>,
    pub created_at: i64,
    pub updated_at: i64,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = user_threat_stats)]
pub struct NewUserThreatStats {
    pub user_id: String,
    pub phishing_count: i32,
    pub malware_count: i32,
    pub cryptojacking_count: i32,
    pub ransomware_count: i32,
    pub scam_count: i32,
    pub data_harvesting_count: i32,
    pub critical_threats: i32,
    pub high_threats: i32,
    pub medium_threats: i32,
    pub low_threats: i32,
    pub total_blocked: i32,
    pub total_warnings: i32,
    pub total_allowed: i32,
}

impl NewUserThreatStats {
    pub fn new(user_id: String) -> Self {
        Self {
            user_id,
            phishing_count: 1,
            malware_count: 0,
            cryptojacking_count: 0,
            ransomware_count: 0,
            scam_count: 0,
            data_harvesting_count: 0,
            critical_threats: 0,
            high_threats: 0,
            medium_threats: 0,
            low_threats: 0,
            total_blocked: 0,
            total_warnings: 0,
            total_allowed: 0,
        }
    }
}

// ==========================================
// USER THREAT SOURCES (Geographic)
// ==========================================

#[derive(Debug, Queryable, Selectable, Identifiable, Associations, Serialize, Deserialize)]
#[diesel(table_name = user_threat_sources)]
#[diesel(belongs_to(User, foreign_key = user_id))]
#[diesel(primary_key(source_id))]
#[diesel(check_for_backend(diesel::sqlite::Sqlite))]
pub struct UserThreatSource {
    pub source_id: String,
    pub user_id: String,
    pub country_code: Option<String>,
    pub country_name: Option<String>,
    pub threat_count: i32,
    pub phishing_count: i32,
    pub last_seen: i64,
    pub created_at: i64,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = user_threat_sources)]
pub struct NewUserThreatSource {
    pub user_id: String,
    pub country_code: Option<String>,
    pub country_name: Option<String>,
    pub threat_count: i32,
    pub phishing_count: i32,
}

// ==========================================
// USER SCAN QUEUE (Queue Management)
// ==========================================

#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize)]
#[diesel(table_name = user_scan_queue)]
#[diesel(primary_key(queue_id))]
pub struct UserScanQueue {
    pub queue_id: String,
    pub user_id: String,
    pub device_fingerprint: String,
    pub encrypted_url: String,
    pub url_hash: String,
    pub status: String,
    pub priority: i32,
    pub retry_count: i32,
    pub max_retries: i32,
    pub queued_at: i64,
    pub started_at: Option<i64>,
    pub completed_at: Option<i64>,
}

// ==========================================
// USER MODEL UPDATES (Version Tracking)
// ==========================================

#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize)]
#[diesel(table_name = user_model_updates)]
#[diesel(primary_key(update_id))]
pub struct UserModelUpdate {
    pub update_id: String,
    pub user_id: String,
    pub device_fingerprint: String,
    pub from_version: Option<String>,
    pub to_version: String,
    pub update_status: String,
    pub update_progress: i32,
    pub download_size_mb: Option<f64>,
    pub download_speed_mbps: Option<f64>,
    pub install_time_ms: Option<f64>,
    pub error_message: Option<String>,
    pub initiated_at: i64,
    pub completed_at: Option<i64>,
}

// ==========================================
// USER PRIVACY SETTINGS
// ==========================================

#[derive(Debug, Queryable, Identifiable, Serialize, Deserialize)]
#[diesel(table_name = user_privacy_settings)]
#[diesel(primary_key(user_id))]
pub struct UserPrivacySettings {
    pub user_id: String,
    pub encryption_enabled: i32,
    pub encryption_algorithm: String,
    pub data_retention_days: i32,
    pub auto_delete_enabled: i32,
    pub collect_analytics: i32,
    pub share_threat_intelligence: i32,
    pub allow_geographic_tracking: i32,
    pub last_data_export: Option<i64>,
    pub data_deletion_requested: i32,
    pub data_deletion_scheduled: Option<i64>,
    pub created_at: i64,
    pub updated_at: i64,
}

// ==========================================
// HELPER STRUCTS FOR API RESPONSES
// ==========================================

// Removed: use crate::models::User;

#[derive(Debug, Serialize)]
pub struct ActivityItem {
    pub activity_id: String,
    pub encrypted_url: String,
    pub encryption_nonce: String,
    pub domain: String,
    pub is_phishing: i32,
    pub threat_type: Option<String>,
    pub threat_level: String,
    pub confidence: f64,
    pub action_taken: String,
    pub timestamp: i64,
}

impl From<UserActivity> for ActivityItem {
    fn from(activity: UserActivity) -> Self {
        Self {
            activity_id: activity.activity_id.to_string(),
            encrypted_url: activity.encrypted_url,
            encryption_nonce: activity.encryption_nonce,
            domain: "[ENCRYPTED]".to_string(),
            is_phishing: activity.is_phishing,
            threat_type: activity.threat_type,
            threat_level: activity.threat_level,
            confidence: activity.confidence.unwrap_or(0.0),
            action_taken: activity.action_taken,
            timestamp: activity.timestamp,
        }
    }
}

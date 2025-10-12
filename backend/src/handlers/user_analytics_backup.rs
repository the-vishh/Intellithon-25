// 📊 USER PERSONAL ANALYTICS API
// Real-time user-specific statistics with E2E encryption

use actix_web::{web, HttpResponse, Result as ActixResult};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

use crate::db::DbPool;
use crate::db::models_analytics::*;
use crate::db::schema_analytics::*;

// ==========================================
// REQUEST/RESPONSE MODELS
// ==========================================

#[derive(Debug, Serialize, Deserialize)]
pub struct UserAnalyticsResponse {
    // User identification
    pub user_id: String,
    pub device_fingerprint: String,

    // Real-time statistics
    pub total_threats_blocked: i64,
    pub activities_last_24h: i64,
    pub threats_last_24h: i64,

    // Recent activity feed (last 20 activities)
    pub recent_activities: Vec<ActivityItem>,

    // Device-specific performance
    pub device_performance: DevicePerformance,

    // Threat distribution for THIS user
    pub threat_breakdown: ThreatBreakdown,

    // Geographic threat sources
    pub threat_sources: Vec<ThreatSource>,

    // Scan queue status
    pub scan_queue: ScanQueueStatus,

    // Model information
    pub model_info: ModelInfo,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ActivityItem {
    pub activity_id: String,
    pub url: String,  // Decrypted client-side
    pub encrypted_url: String,  // For client-side decryption
    pub domain: String,
    pub is_phishing: bool,
    pub threat_type: Option<String>,
    pub threat_level: String,
    pub confidence: f64,
    pub action_taken: String,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DevicePerformance {
    pub processing_speed_ms: f64,
    pub memory_usage_mb: f64,
    pub cache_hit_rate: f64,
    pub local_db_size_mb: f64,
    pub pending_scans: i32,
    pub failed_scans: i32,
    pub meets_target: bool,  // <100ms target
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ThreatBreakdown {
    pub phishing: i64,
    pub malware: i64,
    pub cryptojacking: i64,
    pub ransomware: i64,
    pub scam: i64,
    pub data_harvesting: i64,

    // Severity
    pub critical: i64,
    pub high: i64,
    pub medium: i64,
    pub low: i64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ThreatSource {
    pub country_code: String,
    pub country_name: String,
    pub threat_count: i64,
    pub percentage: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ScanQueueStatus {
    pub pending: i32,
    pub processing: i32,
    pub failed: i32,
    pub avg_wait_time_ms: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ModelInfo {
    pub version: String,
    pub last_updated: DateTime<Utc>,
    pub size_mb: f64,
    pub update_available: bool,
    pub next_version: Option<String>,
}

// ==========================================
// API ENDPOINTS
// ==========================================

/// GET /api/user/{user_id}/analytics
/// Returns comprehensive real-time user analytics
pub async fn get_user_analytics(
    user_id: web::Path<Uuid>,
    device_fp: web::Query<DeviceQuery>,
    db_pool: web::Data<DbPool>,
) -> Result<HttpResponse> {
    let user_id = user_id.into_inner();
    let device_fingerprint = device_fp.device_fingerprint.clone();

    let analytics = web::block(move || {
        let mut conn = db_pool.get().expect("Failed to get DB connection");

        // Get user's recent activities (last 20)
        let recent_activities = get_recent_activities(&mut conn, &user_id, 20)?;

        // Get device performance metrics
        let device_performance = get_device_performance(&mut conn, &user_id, &device_fingerprint)?;

        // Get threat breakdown
        let threat_breakdown = get_threat_breakdown(&mut conn, &user_id)?;

        // Get threat sources by geography
        let threat_sources = get_threat_sources(&mut conn, &user_id)?;

        // Get scan queue status
        let scan_queue = get_scan_queue_status(&mut conn, &user_id, &device_fingerprint)?;

        // Get model information
        let model_info = get_model_info(&mut conn, &user_id, &device_fingerprint)?;

        // Count threats blocked
        let total_threats: i64 = user_activity::table
            .filter(user_activity::user_id.eq(user_id))
            .filter(user_activity::is_phishing.eq(true))
            .count()
            .get_result(&mut conn)?;

        // Count activities last 24h
        let activities_24h: i64 = user_activity::table
            .filter(user_activity::user_id.eq(user_id))
            .filter(user_activity::timestamp.gt(Utc::now() - Duration::hours(24)))
            .count()
            .get_result(&mut conn)?;

        // Count threats last 24h
        let threats_24h: i64 = user_activity::table
            .filter(user_activity::user_id.eq(user_id))
            .filter(user_activity::is_phishing.eq(true))
            .filter(user_activity::timestamp.gt(Utc::now() - Duration::hours(24)))
            .count()
            .get_result(&mut conn)?;

        Ok::<UserAnalyticsResponse, diesel::result::Error>(UserAnalyticsResponse {
            user_id: user_id.to_string(),
            device_fingerprint: device_fingerprint.clone(),
            total_threats_blocked: total_threats,
            activities_last_24h: activities_24h,
            threats_last_24h: threats_24h,
            recent_activities,
            device_performance,
            threat_breakdown,
            threat_sources,
            scan_queue,
            model_info,
        })
    })
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

    Ok(HttpResponse::Ok().json(analytics))
}

/// GET /api/user/{user_id}/threats/live
/// WebSocket endpoint for real-time threat feed
pub async fn get_live_threats(
    user_id: web::Path<Uuid>,
    db_pool: web::Data<DbPool>,
) -> Result<HttpResponse> {
    // TODO: Implement WebSocket connection
    // For now, return last 10 threats

    let user_id = user_id.into_inner();

    let threats = web::block(move || {
        let mut conn = db_pool.get().expect("Failed to get DB connection");

        use crate::db::schema::user_activity::dsl::*;

        user_activity
            .filter(user_id.eq(user_id))
            .filter(is_phishing.eq(true))
            .order(timestamp.desc())
            .limit(10)
            .load::<UserActivity>(&mut conn)
    })
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

    Ok(HttpResponse::Ok().json(threats))
}

/// POST /api/user/{user_id}/activity
/// Log new user activity (called by extension on every scan)
pub async fn log_user_activity(
    user_id: web::Path<Uuid>,
    activity: web::Json<LogActivityRequest>,
    db_pool: web::Data<DbPool>,
) -> Result<HttpResponse> {
    let user_id = user_id.into_inner();
    let activity_data = activity.into_inner();

    // Encrypt sensitive data (URL, domain)
    let encryption_key = UserEncryptionKey::from_user_id(&user_id.to_string());

    let encrypted_url = encryption_key.encrypt(&activity_data.url)
        .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

    let encrypted_domain = encryption_key.encrypt(&activity_data.domain)
        .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

    let url_hash = hash_for_indexing(&activity_data.url);
    let domain_hash = hash_for_indexing(&activity_data.domain);

    let activity_id = web::block(move || {
        let mut conn = db_pool.get().expect("Failed to get DB connection");

        use crate::db::schema::user_activity;

        let new_activity = NewUserActivity {
            user_id,
            encrypted_url: encrypted_url.ciphertext,
            url_hash,
            encrypted_domain: encrypted_domain.ciphertext,
            domain_hash,
            is_phishing: activity_data.is_phishing,
            threat_type: activity_data.threat_type,
            threat_level: activity_data.threat_level,
            confidence: activity_data.confidence,
            action_taken: activity_data.action_taken,
            encryption_nonce: encrypted_url.nonce,
        };

        diesel::insert_into(user_activity::table)
            .values(&new_activity)
            .returning(user_activity::activity_id)
            .get_result::<Uuid>(&mut conn)
    })
    .await
    .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

    Ok(HttpResponse::Created().json(serde_json::json!({
        "activity_id": activity_id,
        "status": "logged",
        "encrypted": true
    })))
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================

fn get_recent_activities(
    conn: &mut PgConnection,
    user_id: &Uuid,
    limit: i64,
) -> Result<Vec<ActivityItem>, diesel::result::Error> {
    use crate::db::schema::user_activity::dsl::*;

    let activities = user_activity
        .filter(user_id.eq(user_id))
        .order(timestamp.desc())
        .limit(limit)
        .load::<UserActivity>(conn)?;

    // Convert to ActivityItem (URLs remain encrypted, client decrypts)
    Ok(activities.into_iter().map(|a| ActivityItem {
        activity_id: a.activity_id.to_string(),
        url: "[ENCRYPTED]".to_string(),  // Client will decrypt
        encrypted_url: a.encrypted_url.clone(),
        domain: "[ENCRYPTED]".to_string(),
        is_phishing: a.is_phishing,
        threat_type: a.threat_type,
        threat_level: a.threat_level,
        confidence: a.confidence.unwrap_or(0.0),
        action_taken: a.action_taken,
        timestamp: a.timestamp,
    }).collect())
}

fn get_device_performance(
    conn: &mut PgConnection,
    user_id: &Uuid,
    device_fp: &str,
) -> Result<DevicePerformance, diesel::result::Error> {
    use crate::db::schema::device_metrics::dsl::*;

    let metrics = device_metrics
        .filter(user_id.eq(user_id))
        .filter(device_fingerprint.eq(device_fp))
        .first::<DeviceMetrics>(conn)
        .optional()?;

    match metrics {
        Some(m) => Ok(DevicePerformance {
            processing_speed_ms: m.avg_processing_speed_ms.unwrap_or(0.0),
            memory_usage_mb: m.memory_usage_mb.unwrap_or(0.0),
            cache_hit_rate: m.cache_hit_rate.unwrap_or(0.0),
            local_db_size_mb: m.local_db_size_mb.unwrap_or(0.0),
            pending_scans: m.pending_scans.unwrap_or(0),
            failed_scans: m.failed_scans.unwrap_or(0),
            meets_target: m.avg_processing_speed_ms.unwrap_or(999.0) < 100.0,
        }),
        None => Ok(DevicePerformance {
            processing_speed_ms: 0.0,
            memory_usage_mb: 0.0,
            cache_hit_rate: 0.0,
            local_db_size_mb: 0.0,
            pending_scans: 0,
            failed_scans: 0,
            meets_target: false,
        }),
    }
}

fn get_threat_breakdown(
    conn: &mut PgConnection,
    user_id: &Uuid,
) -> Result<ThreatBreakdown, diesel::result::Error> {
    use crate::db::schema::user_activity::dsl::*;

    // Count by threat type
    let phishing_count: i64 = user_activity
        .filter(user_id.eq(user_id))
        .filter(threat_type.eq("phishing"))
        .count()
        .get_result(conn)?;

    let malware_count: i64 = user_activity
        .filter(user_id.eq(user_id))
        .filter(threat_type.eq("malware"))
        .count()
        .get_result(conn)?;

    // Count by severity
    let critical_count: i64 = user_activity
        .filter(user_id.eq(user_id))
        .filter(threat_level.eq("CRITICAL"))
        .count()
        .get_result(conn)?;

    Ok(ThreatBreakdown {
        phishing: phishing_count,
        malware: malware_count,
        cryptojacking: 0,  // TODO: Implement other types
        ransomware: 0,
        scam: 0,
        data_harvesting: 0,
        critical: critical_count,
        high: 0,  // TODO: Count other severities
        medium: 0,
        low: 0,
    })
}

fn get_threat_sources(
    conn: &mut PgConnection,
    user_id: &Uuid,
) -> Result<Vec<ThreatSource>, diesel::result::Error> {
    use crate::db::schema::user_threat_sources::dsl::*;

    let sources = user_threat_sources
        .filter(user_id.eq(user_id))
        .order(threat_count.desc())
        .limit(10)
        .load::<UserThreatSource>(conn)?;

    let total_threats: i64 = sources.iter().map(|s| s.threat_count).sum();

    Ok(sources.into_iter().map(|s| ThreatSource {
        country_code: s.country_code,
        country_name: s.country_name,
        threat_count: s.threat_count,
        percentage: (s.threat_count as f64 / total_threats as f64) * 100.0,
    }).collect())
}

fn get_scan_queue_status(
    conn: &mut PgConnection,
    user_id: &Uuid,
    device_fp: &str,
) -> Result<ScanQueueStatus, diesel::result::Error> {
    use crate::db::schema::user_scan_queue::dsl::*;

    let pending_count: i64 = user_scan_queue
        .filter(user_id.eq(user_id))
        .filter(status.eq("pending"))
        .count()
        .get_result(conn)?;

    let processing_count: i64 = user_scan_queue
        .filter(user_id.eq(user_id))
        .filter(status.eq("processing"))
        .count()
        .get_result(conn)?;

    let failed_count: i64 = user_scan_queue
        .filter(user_id.eq(user_id))
        .filter(status.eq("failed"))
        .count()
        .get_result(conn)?;

    Ok(ScanQueueStatus {
        pending: pending_count as i32,
        processing: processing_count as i32,
        failed: failed_count as i32,
        avg_wait_time_ms: 0.0,  // TODO: Calculate from queue data
    })
}

fn get_model_info(
    conn: &mut PgConnection,
    user_id: &Uuid,
    device_fp: &str,
) -> Result<ModelInfo, diesel::result::Error> {
    use crate::db::schema::device_metrics::dsl::*;

    let metrics = device_metrics
        .filter(user_id.eq(user_id))
        .filter(device_fingerprint.eq(device_fp))
        .first::<DeviceMetrics>(conn)
        .optional()?;

    match metrics {
        Some(m) => Ok(ModelInfo {
            version: m.model_version.unwrap_or("1.0.0".to_string()),
            last_updated: m.model_last_updated.unwrap_or(Utc::now()),
            size_mb: m.model_size_mb.unwrap_or(0.0),
            update_available: false,  // TODO: Check for updates
            next_version: None,
        }),
        None => Ok(ModelInfo {
            version: "1.0.0".to_string(),
            last_updated: Utc::now(),
            size_mb: 0.0,
            update_available: false,
            next_version: None,
        }),
    }
}

// ==========================================
// REQUEST MODELS
// ==========================================

#[derive(Debug, Deserialize)]
pub struct DeviceQuery {
    pub device_fingerprint: String,
}

#[derive(Debug, Deserialize)]
pub struct LogActivityRequest {
    pub url: String,
    pub domain: String,
    pub is_phishing: bool,
    pub threat_type: Option<String>,
    pub threat_level: String,
    pub confidence: f64,
    pub action_taken: String,
}

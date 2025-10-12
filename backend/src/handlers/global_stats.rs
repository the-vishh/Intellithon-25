/*!
 * Global statistics endpoints
 *
 * NOTE: Temporarily returns mock data while migrating to SQLite
 * TODO: Reimplement with user_activity and user_threat_stats tables
 */

use actix_web::{web, HttpResponse};
use serde::Serialize;
use uuid::Uuid;

use crate::db::DbPool;

#[derive(Debug, Serialize)]
pub struct GlobalStatsResponse {
    pub total_users: i32,
    pub active_users: i32,
    pub total_scans: i32,
    pub threats_blocked: i32,
    pub scans_last_hour: i32,
    pub scans_last_24h: i32,
    pub threats_last_24h: i32,
    pub avg_confidence: f64,
    pub avg_latency_ms: f64,
    pub model_accuracy: Option<f64>,
    pub model_precision: Option<f64>,
    pub model_recall: Option<f64>,
    pub sensitivity_breakdown: SensitivityBreakdown,
    pub threat_breakdown: ThreatBreakdown,
    pub top_phishing_domains: Vec<DomainCount>,
}

#[derive(Debug, Serialize)]
pub struct SensitivityBreakdown {
    pub conservative: i32,
    pub balanced: i32,
    pub aggressive: i32,
}

#[derive(Debug, Serialize)]
pub struct ThreatBreakdown {
    pub critical: i32,
    pub high: i32,
    pub medium: i32,
    pub low: i32,
    pub safe: i32,
}

#[derive(Debug, Serialize)]
pub struct DomainCount {
    pub domain: String,
    pub count: i64,
}

#[derive(Debug, Serialize)]
pub struct UserStatsResponse {
    pub user_id: Uuid,
    pub total_scans: i32,
    pub threats_blocked: i32,
    pub last_scan: Option<chrono::DateTime<chrono::Utc>>,
    pub sensitivity_mode: String,
    pub avg_latency_ms: f64,
    pub scans_today: i32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

/// GET /api/stats/global
/// Returns aggregated statistics across all users
/// TEMP: Returns mock data during SQLite migration
pub async fn get_global_stats(_pool: web::Data<DbPool>) -> HttpResponse {
    // TODO: Reimplement with user_activity table after SQLite migration complete
    log::info!("📊 Returning mock global stats (SQLite migration in progress)");

    let mock_stats = GlobalStatsResponse {
        total_users: 0,
        active_users: 0,
        total_scans: 0,
        threats_blocked: 0,
        scans_last_hour: 0,
        scans_last_24h: 0,
        threats_last_24h: 0,
        avg_confidence: 0.0,
        avg_latency_ms: 0.0,
        model_accuracy: None,
        model_precision: None,
        model_recall: None,
        sensitivity_breakdown: SensitivityBreakdown {
            conservative: 0,
            balanced: 0,
            aggressive: 0,
        },
        threat_breakdown: ThreatBreakdown {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0,
            safe: 0,
        },
        top_phishing_domains: vec![],
    };

    HttpResponse::Ok().json(mock_stats)
}

// Old implementation - commented out during SQLite migration
/*
pub async fn get_global_stats_OLD(_pool: web::Data<DbPool>) -> HttpResponse {
    use schema::{users, scans};

    let mut conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            log::error!("Failed to get DB connection: {}", e);
            return HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Database connection failed"
            }));
        }
    };

    // Query global statistics
    let stats = web::block(move || {
        // Total users
        let total_users: i64 = users::table
            .filter(users::is_active.eq(true))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Active users (last 24h)
        let active_users: i64 = users::table
            .filter(users::last_active_at.gt(chrono::Utc::now() - chrono::Duration::hours(24)))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Total scans
        let total_scans: i64 = scans::table
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Threats blocked
        let threats_blocked: i64 = scans::table
            .filter(scans::is_phishing.eq(true))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Scans last hour
        let scans_last_hour: i64 = scans::table
            .filter(scans::scanned_at.gt(chrono::Utc::now() - chrono::Duration::hours(1)))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Scans last 24h
        let scans_last_24h: i64 = scans::table
            .filter(scans::scanned_at.gt(chrono::Utc::now() - chrono::Duration::hours(24)))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Threats last 24h
        let threats_last_24h: i64 = scans::table
            .filter(scans::is_phishing.eq(true))
            .filter(scans::scanned_at.gt(chrono::Utc::now() - chrono::Duration::hours(24)))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Average confidence
        let avg_confidence: Option<f64> = scans::table
            .select(diesel::dsl::avg(scans::confidence))
            .first(&mut conn)
            .unwrap_or(None);

        // Average latency
        let avg_latency: Option<f64> = scans::table
            .select(diesel::dsl::avg(scans::latency_ms))
            .first(&mut conn)
            .unwrap_or(None);

        // Sensitivity breakdown
        let conservative_count: i64 = scans::table
            .filter(scans::sensitivity_mode.eq("conservative"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        let balanced_count: i64 = scans::table
            .filter(scans::sensitivity_mode.eq("balanced"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        let aggressive_count: i64 = scans::table
            .filter(scans::sensitivity_mode.eq("aggressive"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Threat breakdown
        let critical_count: i64 = scans::table
            .filter(scans::threat_level.eq("CRITICAL"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        let high_count: i64 = scans::table
            .filter(scans::threat_level.eq("HIGH"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        let medium_count: i64 = scans::table
            .filter(scans::threat_level.eq("MEDIUM"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        let low_count: i64 = scans::table
            .filter(scans::threat_level.eq("LOW"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        let safe_count: i64 = scans::table
            .filter(scans::threat_level.eq("SAFE"))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        // Top phishing domains (TODO: Implement with GROUP BY)
        let top_domains = vec![];

        Ok::<GlobalStatsResponse, diesel::result::Error>(GlobalStatsResponse {
            total_users: total_users as i32,
            active_users: active_users as i32,
            total_scans: total_scans as i32,
            threats_blocked: threats_blocked as i32,
            scans_last_hour: scans_last_hour as i32,
            scans_last_24h: scans_last_24h as i32,
            threats_last_24h: threats_last_24h as i32,
            avg_confidence: avg_confidence.unwrap_or(0.0),
            avg_latency_ms: avg_latency.unwrap_or(0.0),
            model_accuracy: None, // TODO: Calculate from model_metrics table
            model_precision: None,
            model_recall: None,
            sensitivity_breakdown: SensitivityBreakdown {
                conservative: conservative_count as i32,
                balanced: balanced_count as i32,
                aggressive: aggressive_count as i32,
            },
            threat_breakdown: ThreatBreakdown {
                critical: critical_count as i32,
                high: high_count as i32,
                medium: medium_count as i32,
                low: low_count as i32,
                safe: safe_count as i32,
            },
            top_phishing_domains: top_domains,
        })
    })
    .await;

    match stats {
        Ok(Ok(stats)) => {
            log::info!("✅ Global stats retrieved: {} users, {} scans",
                stats.total_users, stats.total_scans);
            HttpResponse::Ok().json(stats)
        }
        Ok(Err(e)) => {
            log::error!("❌ Database query error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Failed to query statistics"
            }))
        }
        Err(e) => {
            log::error!("❌ Blocking error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Internal server error"
            }))
        }
    }
}
*/

/// GET /api/stats/user/{user_id}
/// Returns statistics for specific user
/// TEMP: Returns mock data during SQLite migration
pub async fn get_user_stats(
    _pool: web::Data<DbPool>,
    user_id: web::Path<Uuid>,
) -> HttpResponse {
    let uid = user_id.into_inner();
    log::info!("📊 Returning mock user stats (SQLite migration in progress)");

    let mock_stats = UserStatsResponse {
        user_id: uid,
        total_scans: 0,
        threats_blocked: 0,
        last_scan: None,
        sensitivity_mode: "balanced".to_string(),
        avg_latency_ms: 0.0,
        scans_today: 0,
        created_at: chrono::Utc::now(),
    };

    HttpResponse::Ok().json(mock_stats)
}

// Old implementation
/*
pub async fn get_user_stats_OLD(
    pool: web::Data<DbPool>,
    user_id: web::Path<Uuid>,
) -> HttpResponse {
    use schema::{users, scans};

    let user_id = user_id.into_inner();

    let mut conn = match pool.get() {
        Ok(conn) => conn,
        Err(e) => {
            log::error!("Failed to get DB connection: {}", e);
            return HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Database connection failed"
            }));
        }
    };

    let stats = web::block(move || {
        // Get user
        let user: crate::db::User = users::table
            .find(user_id)
            .first(&mut conn)?;

        // Get last scan
        let last_scan: Option<chrono::DateTime<chrono::Utc>> = scans::table
            .filter(scans::user_id.eq(user_id))
            .select(scans::scanned_at)
            .order(scans::scanned_at.desc())
            .first(&mut conn)
            .ok();

        // Scans today
        let scans_today: i64 = scans::table
            .filter(scans::user_id.eq(user_id))
            .filter(scans::scanned_at.gt(chrono::Utc::now().date_naive().and_hms_opt(0, 0, 0).unwrap().and_utc()))
            .count()
            .get_result(&mut conn)
            .unwrap_or(0);

        Ok::<UserStatsResponse, diesel::result::Error>(UserStatsResponse {
            user_id: user.user_id,
            total_scans: user.total_scans,
            threats_blocked: user.total_threats_blocked,
            last_scan,
            sensitivity_mode: user.sensitivity_mode,
            avg_latency_ms: user.average_response_time_ms,
            scans_today: scans_today as i32,
            created_at: user.created_at,
        })
    })
    .await;

    match stats {
        Ok(Ok(stats)) => {
            log::info!("✅ User stats retrieved for {}", user_id);
            HttpResponse::Ok().json(stats)
        }
        Ok(Err(e)) => {
            log::error!("❌ Database query error: {}", e);
            HttpResponse::NotFound().json(serde_json::json!({
                "error": "User not found"
            }))
        }
        Err(e) => {
            log::error!("❌ Blocking error: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Internal server error"
            }))
        }
    }
}
*/

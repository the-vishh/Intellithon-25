/*!
 * Statistics endpoint
 */

use actix_web::{web, HttpResponse};

use crate::{AppState, models::StatsResponse};

/// Get cache statistics
///
/// GET /api/stats
pub async fn get_stats(data: web::Data<AppState>) -> HttpResponse {
    let mut cache = data.cache.clone();

    match cache.get_stats().await {
        Ok((hits, misses)) => {
            let total = hits + misses;
            let hit_rate = if total > 0 {
                (hits as f64 / total as f64) * 100.0
            } else {
                0.0
            };

            HttpResponse::Ok().json(StatsResponse {
                total_requests: total as u64,
                cache_hits: hits as u64,
                cache_misses: misses as u64,
                cache_hit_rate: hit_rate,
                average_latency_ms: 0.0, // TODO: track this
            })
        }
        Err(e) => {
            log::error!("Failed to get stats: {}", e);
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": "Failed to retrieve statistics"
            }))
        }
    }
}

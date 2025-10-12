/*!
 * URL checking endpoint handler
 */

use actix_web::{web, HttpResponse};
use std::time::Instant;

use crate::{AppState, models::{URLCheckRequest, ErrorResponse}};

/// Check if URL is phishing
///
/// POST /api/check-url
/// Body: {"url": "https://example.com"}
pub async fn check_url(
    req: web::Json<URLCheckRequest>,
    data: web::Data<AppState>,
) -> HttpResponse {
    let start = Instant::now();
    let url = &req.url;

    log::info!("🔍 Checking URL: {}", url);

    // Validate URL
    if url.is_empty() || url.len() < 10 {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "invalid_url".to_string(),
            message: "URL must be at least 10 characters".to_string(),
            timestamp: chrono::Utc::now(),
        });
    }

    // Check cache first
    let mut cache = data.cache.clone();
    match cache.get(url).await {
        Ok(Some(mut cached_result)) => {
            cached_result.cached = true;
            let elapsed = start.elapsed().as_millis() as f64;
            log::info!("✅ Cache HIT: {} ({}ms)", url, elapsed);
            return HttpResponse::Ok().json(cached_result);
        }
        Ok(None) => {
            log::debug!("Cache miss, calling ML service...");
        }
        Err(e) => {
            log::warn!("Cache error: {}, falling back to ML service", e);
        }
    }

    // Cache miss - call ML service
    let sensitivity_mode = req.sensitivity_mode.as_str();
    match data.ml_client.predict(url, sensitivity_mode).await {
        Ok(result) => {
            let elapsed = start.elapsed().as_millis() as f64;
            log::info!("✅ ML prediction: {} - {} (confidence: {:.2}%, threshold: {:.2}, mode: {}) in {}ms",
                url, result.threat_level, result.confidence * 100.0, result.threshold_used, result.sensitivity_mode, elapsed);

            // Cache the result
            let ttl = if result.is_phishing {
                7 * 24 * 60 * 60  // 7 days for phishing URLs
            } else {
                24 * 60 * 60  // 24 hours for safe URLs
            };

            if let Err(e) = cache.set(url, &result, ttl).await {
                log::warn!("Failed to cache result: {}", e);
            }

            HttpResponse::Ok().json(result)
        }
        Err(e) => {
            log::error!("❌ ML service error for {}: {}", url, e);
            HttpResponse::InternalServerError().json(ErrorResponse {
                error: "ml_service_error".to_string(),
                message: format!("Failed to analyze URL: {}", e),
                timestamp: chrono::Utc::now(),
            })
        }
    }
}

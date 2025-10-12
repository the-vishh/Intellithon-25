/*!
 * Root endpoint
 */

use actix_web::HttpResponse;

/// Root endpoint
///
/// GET /
pub async fn root() -> HttpResponse {
    HttpResponse::Ok().json(serde_json::json!({
        "service": "Phishing Detection API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "check_url": "POST /api/check-url",
            "stats": "GET /api/stats"
        },
        "documentation": "See README.md for API documentation"
    }))
}

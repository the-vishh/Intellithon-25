/*!
 * 🚀 PHISHING DETECTION API GATEWAY - RUST
 * ==========================================
 *
 * High-performance API gateway with Redis caching and rate limiting.
 *
 * Architecture:
 * - Chrome Extension → Rust API (port 8080)
 * - Rust API → Redis Cache (check first)
 * - Rust API → Python ML Service (port 8000) if cache miss
 * - Response cached for 24 hours
 *
 * Performance Targets:
 * - Cache hit: <10ms
 * - Cache miss: <100ms
 * - Throughput: 10,000+ req/s
 * - P99 latency: <200ms
 */

use actix_web::{web, App, HttpServer, middleware};
use actix_cors::Cors;
use std::env;

mod handlers;
mod services;
mod models;
mod db;
mod crypto;
#[path = "middleware/mod.rs"]
mod custom_middleware;

use services::cache::CacheService;
use services::ml_client::MLClient;
use services::geoip::GeoIPService;
use db::DbPool;
use std::sync::Arc;

/// Application state shared across handlers
pub struct AppState {
    cache: CacheService,
    ml_client: MLClient,
    db_pool: DbPool,
    geoip: Option<Arc<GeoIPService>>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    log::info!("{}", "=".repeat(80));
    log::info!("🚀 STARTING PHISHING DETECTION API GATEWAY");
    log::info!("{}", "=".repeat(80));

    // Load configuration
    dotenv::dotenv().ok();
    let host = env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let redis_url = env::var("REDIS_URL").unwrap_or_else(|_| "redis://127.0.0.1:6379".to_string());
    let ml_service_url = env::var("ML_SERVICE_URL")
        .unwrap_or_else(|_| "http://127.0.0.1:8000".to_string());

    log::info!("📊 Configuration:");
    log::info!("   API Gateway: {}:{}", host, port);
    log::info!("   Redis: {}", redis_url);
    log::info!("   ML Service: {}", ml_service_url);

    // Initialize services
    log::info!("🔧 Initializing services...");

    let cache = CacheService::new(&redis_url).await
        .expect("Failed to connect to Redis");
    log::info!("✅ Redis connected");

    let ml_client = MLClient::new(&ml_service_url);
    log::info!("✅ ML client initialized");

    // Initialize GeoIP service (optional)
    let geoip = match GeoIPService::new("geodb/GeoLite2-City.mmdb") {
        Ok(service) => {
            log::info!("✅ GeoIP database loaded (GeoLite2-City)");
            Some(Arc::new(service))
        }
        Err(e) => {
            log::warn!("⚠️  GeoIP database not available: {}", e);
            log::warn!("⚠️  Geographic threat tracking disabled");
            None
        }
    };

    // Initialize database connection pool with timeout to prevent hanging
    let db_pool = match db::create_pool_with_timeout(std::time::Duration::from_secs(5)) {
        Ok(pool) => {
            log::info!("✅ Database connected");
            pool
        }
        Err(e) => {
            log::warn!("⚠️  Database connection failed: {}", e);
            log::warn!("⚠️  Running WITHOUT database. Analytics will NOT be saved.");
            log::warn!("⚠️  To enable: Run ./setup_sqlite.sh to create database");

            // Create a pool with a non-existent database to avoid connection attempts
            let dummy_url = ":memory:"; // SQLite in-memory database
            let manager = diesel::r2d2::ConnectionManager::<diesel::sqlite::SqliteConnection>::new(dummy_url);
            diesel::r2d2::Pool::builder()
                .max_size(1)
                .min_idle(Some(0))
                .connection_timeout(std::time::Duration::from_millis(100))
                .test_on_check_out(false) // Don't test connections
                .build(manager)
                .expect("Failed to create dummy pool")
        }
    };

    // Create shared application state
    let app_state = web::Data::new(AppState {
        cache,
        ml_client,
        db_pool: db_pool.clone(),
        geoip,
    });

    // Also share db_pool separately for stats endpoints
    let db_pool_data = web::Data::new(db_pool);

    let bind_address = format!("{}:{}", host, port);
    log::info!("🚀 Starting server on {}", bind_address);
    log::info!("📚 API Documentation: http://localhost:{}/api/docs", port);
    log::info!("❤️  Health Check: http://localhost:{}/health", port);

    // Start HTTP server
    HttpServer::new(move || {
        // Configure CORS
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            .app_data(app_state.clone())
            .app_data(db_pool_data.clone())
            .wrap(cors)
            .wrap(middleware::Logger::default())
            .wrap(middleware::Compress::default())
            .wrap(custom_middleware::rate_limit::RateLimitMiddleware)
            // Routes
            .service(
                web::scope("/api")
                    .route("/check-url", web::post().to(handlers::url_check::check_url))
                    .route("/stats", web::get().to(handlers::stats::get_stats))
                    .route("/stats/global", web::get().to(handlers::global_stats::get_global_stats))
                    .route("/stats/user/{user_id}", web::get().to(handlers::global_stats::get_user_stats))
                    // 📊 User Analytics Endpoints (NEW)
                    .route("/user/{user_id}/analytics", web::get().to(handlers::user_analytics::get_user_analytics))
                    .route("/user/{user_id}/activity", web::post().to(handlers::user_analytics::log_activity))
                    .route("/user/{user_id}/threats/live", web::get().to(handlers::user_analytics::live_threats))
            )
            .route("/health", web::get().to(handlers::health::health_check))
            .route("/", web::get().to(handlers::root::root))
    })
    .bind(bind_address)?
    .run()
    .await
}

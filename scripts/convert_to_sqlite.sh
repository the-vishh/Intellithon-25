#!/bin/bash
# Complete SQLite Conversion Script
# This will convert all PostgreSQL types to SQLite types

echo "========================================"
echo "🔧 SQLite Conversion Starting..."
echo "========================================"
echo ""

cd backend

# Step 1: Replace schema.rs with SQLite version
echo "Step 1: Updating schema.rs..."
cat > src/db/schema.rs << 'EOF'
// @generated automatically for SQLite
// PhishGuard Database Schema

diesel::table! {
    users (user_id) {
        user_id -> Text,
        created_at -> Integer,
    }
}

diesel::table! {
    user_activity (activity_id) {
        activity_id -> Text,
        user_id -> Text,
        encrypted_url -> Text,
        url_hash -> Text,
        encrypted_domain -> Text,
        domain_hash -> Text,
        is_phishing -> Integer,
        threat_type -> Nullable<Text>,
        threat_level -> Text,
        confidence -> Nullable<Double>,
        action_taken -> Text,
        user_override -> Integer,
        encryption_nonce -> Text,
        timestamp -> Integer,
    }
}

diesel::table! {
    device_metrics (metric_id) {
        metric_id -> Text,
        user_id -> Text,
        device_fingerprint -> Text,
        browser -> Nullable<Text>,
        os -> Nullable<Text>,
        processing_speed_ms -> Double,
        memory_usage_mb -> Double,
        cache_hit_rate -> Double,
        local_db_size_mb -> Double,
        pending_scans -> Integer,
        failed_scans -> Integer,
        meets_performance_target -> Integer,
        last_updated -> Integer,
    }
}

diesel::table! {
    user_threat_stats (stat_id) {
        stat_id -> Text,
        user_id -> Text,
        phishing_count -> Integer,
        malware_count -> Integer,
        cryptojacking_count -> Integer,
        ransomware_count -> Integer,
        scam_count -> Integer,
        data_harvesting_count -> Integer,
        critical_threats -> Integer,
        high_threats -> Integer,
        medium_threats -> Integer,
        low_threats -> Integer,
        total_blocked -> Integer,
        total_warnings -> Integer,
        total_allowed -> Integer,
        period_start -> Nullable<Integer>,
        period_end -> Nullable<Integer>,
        created_at -> Integer,
        updated_at -> Integer,
    }
}

diesel::table! {
    user_threat_sources (source_id) {
        source_id -> Text,
        user_id -> Text,
        country_code -> Nullable<Text>,
        country_name -> Nullable<Text>,
        threat_count -> Integer,
        phishing_count -> Integer,
        last_seen -> Integer,
        created_at -> Integer,
    }
}

diesel::table! {
    user_scan_queue (queue_id) {
        queue_id -> Text,
        user_id -> Text,
        pending_count -> Integer,
        processing_count -> Integer,
        failed_count -> Integer,
        avg_wait_time_ms -> Double,
        oldest_pending_timestamp -> Nullable<Integer>,
        last_updated -> Integer,
    }
}

diesel::table! {
    user_model_updates (update_id) {
        update_id -> Text,
        user_id -> Text,
        current_version -> Text,
        last_updated -> Integer,
        update_available -> Integer,
        new_version -> Nullable<Text>,
        model_size_mb -> Double,
        auto_update_enabled -> Integer,
    }
}

diesel::table! {
    user_privacy_settings (privacy_id) {
        privacy_id -> Text,
        user_id -> Text,
        encryption_enabled -> Integer,
        data_retention_days -> Integer,
        share_anonymous_stats -> Integer,
        allow_geolocation -> Integer,
        data_deletion_scheduled -> Nullable<Integer>,
        created_at -> Integer,
        updated_at -> Integer,
    }
}

diesel::joinable!(user_activity -> users (user_id));
diesel::joinable!(device_metrics -> users (user_id));
diesel::joinable!(user_threat_stats -> users (user_id));
diesel::joinable!(user_threat_sources -> users (user_id));
diesel::joinable!(user_scan_queue -> users (user_id));
diesel::joinable!(user_model_updates -> users (user_id));
diesel::joinable!(user_privacy_settings -> users (user_id));

diesel::allow_tables_to_appear_in_same_query!(
    users,
    user_activity,
    device_metrics,
    user_threat_stats,
    user_threat_sources,
    user_scan_queue,
    user_model_updates,
    user_privacy_settings,
);
EOF

echo "✅ Schema updated"

# Step 2: Update connection.rs
echo "Step 2: Updating connection.rs..."
cat > src/db/connection.rs << 'EOF'
/*!
 * Database connection pool using Diesel + r2d2 (SQLite)
 */

use diesel::sqlite::SqliteConnection;
use diesel::r2d2::{self, ConnectionManager, Pool};
use std::env;

pub type DbPool = Pool<ConnectionManager<SqliteConnection>>;

/// Create database connection pool
pub fn create_pool() -> Result<DbPool, Box<dyn std::error::Error>> {
    create_pool_with_timeout(std::time::Duration::from_secs(30))
}

/// Create database connection pool with custom timeout
pub fn create_pool_with_timeout(timeout: std::time::Duration) -> Result<DbPool, Box<dyn std::error::Error>> {
    let database_url = env::var("DATABASE_URL")
        .unwrap_or_else(|_| "phishguard.db".to_string());

    log::info!("📊 Connecting to SQLite database: {}", database_url);

    let manager = ConnectionManager::<SqliteConnection>::new(database_url);

    let pool = Pool::builder()
        .max_size(10)
        .min_idle(Some(2))
        .connection_timeout(timeout)
        .test_on_check_out(true)
        .build(manager)?;

    // Test the connection immediately
    pool.get().map_err(|e| format!("Could not establish connection: {}", e))?;

    // Enable foreign keys for SQLite
    use diesel::prelude::*;
    let mut conn = pool.get()?;
    diesel::sql_query("PRAGMA foreign_keys = ON;").execute(&mut conn)?;
    diesel::sql_query("PRAGMA journal_mode = WAL;").execute(&mut conn)?;

    Ok(pool)
}

/// Test database connection
pub fn test_connection(pool: &DbPool) -> Result<(), String> {
    match pool.get() {
        Ok(_conn) => {
            log::info!("✅ Database connection pool healthy");
            Ok(())
        }
        Err(e) => {
            log::error!("❌ Database connection failed: {}", e);
            Err(format!("Database connection failed: {}", e))
        }
    }
}
EOF

echo "✅ Connection updated"

# Step 3: Update .env
echo "Step 3: Updating .env..."
sed -i 's|^DATABASE_URL=.*|DATABASE_URL=phishguard.db|' .env
echo "✅ .env updated"

echo ""
echo "========================================"
echo "✅ Conversion Complete!"
echo "========================================"
echo ""
echo "Next: We need to update model files manually"
echo "This involves converting Uuid types to String"
echo "and timestamp types to i32/i64"
echo ""

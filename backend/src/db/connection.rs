/*!
 * Database connection pool using Diesel + r2d2 (SQLite)
 */

use diesel::sqlite::SqliteConnection;
use diesel::r2d2::{ConnectionManager, Pool};
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

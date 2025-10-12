-- 📊 COMPLETE USER ANALYTICS TABLES - SQLite Version
-- All fields needed for the application

PRAGMA foreign_keys = ON;

-- 1. USERS TABLE (Base user info)
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    extension_id TEXT NOT NULL,
    email TEXT,
    username TEXT,
    sensitivity_mode TEXT NOT NULL DEFAULT 'balanced',
    protection_enabled INTEGER NOT NULL DEFAULT 1,
    ai_detection_enabled INTEGER NOT NULL DEFAULT 1,
    subscription_tier TEXT NOT NULL DEFAULT 'free',
    subscription_expires_at INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    last_active_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    total_scans INTEGER NOT NULL DEFAULT 0,
    total_threats_blocked INTEGER NOT NULL DEFAULT 0,
    average_response_time_ms REAL NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    is_banned INTEGER NOT NULL DEFAULT 0,
    ban_reason TEXT
);

-- 2. USER ACTIVITY (Real-time activity feed)
CREATE TABLE IF NOT EXISTS user_activity (
    activity_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    encrypted_url TEXT NOT NULL,
    url_hash TEXT NOT NULL,
    encrypted_domain TEXT NOT NULL,
    domain_hash TEXT NOT NULL,
    is_phishing INTEGER NOT NULL DEFAULT 0,
    threat_type TEXT,
    threat_level TEXT NOT NULL DEFAULT 'unknown',
    confidence REAL,
    action_taken TEXT NOT NULL DEFAULT 'allowed',
    user_override INTEGER NOT NULL DEFAULT 0,
    encryption_nonce TEXT NOT NULL,
    timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_activity_user_timestamp ON user_activity(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_activity_url_hash ON user_activity(url_hash);
CREATE INDEX IF NOT EXISTS idx_user_activity_domain_hash ON user_activity(domain_hash);

-- 3. DEVICE METRICS (Performance tracking)
CREATE TABLE IF NOT EXISTS device_metrics (
    metric_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    device_fingerprint TEXT NOT NULL,
    browser TEXT,
    browser_version TEXT,
    os TEXT,
    extension_version TEXT,
    avg_processing_speed_ms REAL,
    memory_usage_mb REAL,
    cache_hit_rate REAL,
    feature_extraction_ms REAL,
    ml_inference_ms REAL,
    network_latency_ms REAL,
    local_db_size_mb REAL,
    cache_entries INTEGER,
    last_cache_clear INTEGER,
    pending_scans INTEGER,
    failed_scans INTEGER,
    model_version TEXT,
    model_last_updated INTEGER,
    model_size_mb REAL,
    first_seen INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    last_updated INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_device_metrics_user ON device_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_device_metrics_fingerprint ON device_metrics(device_fingerprint);

-- 4. USER THREAT STATS (Threat breakdown)
CREATE TABLE IF NOT EXISTS user_threat_stats (
    stat_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    phishing_count INTEGER NOT NULL DEFAULT 0,
    malware_count INTEGER NOT NULL DEFAULT 0,
    cryptojacking_count INTEGER NOT NULL DEFAULT 0,
    ransomware_count INTEGER NOT NULL DEFAULT 0,
    scam_count INTEGER NOT NULL DEFAULT 0,
    data_harvesting_count INTEGER NOT NULL DEFAULT 0,
    critical_threats INTEGER NOT NULL DEFAULT 0,
    high_threats INTEGER NOT NULL DEFAULT 0,
    medium_threats INTEGER NOT NULL DEFAULT 0,
    low_threats INTEGER NOT NULL DEFAULT 0,
    total_blocked INTEGER NOT NULL DEFAULT 0,
    total_warnings INTEGER NOT NULL DEFAULT 0,
    total_allowed INTEGER NOT NULL DEFAULT 0,
    period_start INTEGER,
    period_end INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_threat_stats_user ON user_threat_stats(user_id);

-- 5. USER THREAT SOURCES (Geographic origins - GeoIP)
CREATE TABLE IF NOT EXISTS user_threat_sources (
    source_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    country_code TEXT,
    country_name TEXT,
    threat_count INTEGER NOT NULL DEFAULT 1,
    phishing_count INTEGER NOT NULL DEFAULT 0,
    last_seen INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_threat_sources_user ON user_threat_sources(user_id);
CREATE INDEX IF NOT EXISTS idx_user_threat_sources_country ON user_threat_sources(country_code);

-- 6. USER SCAN QUEUE (Queue status)
CREATE TABLE IF NOT EXISTS user_scan_queue (
    queue_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    pending_count INTEGER NOT NULL DEFAULT 0,
    processing_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    avg_wait_time_ms REAL NOT NULL DEFAULT 0,
    oldest_pending_timestamp INTEGER,
    last_updated INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_scan_queue_user ON user_scan_queue(user_id);

-- 7. USER MODEL UPDATES (Model version tracking)
CREATE TABLE IF NOT EXISTS user_model_updates (
    update_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    current_version TEXT NOT NULL DEFAULT '1.0.0',
    last_updated INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    update_available INTEGER NOT NULL DEFAULT 0,
    new_version TEXT,
    model_size_mb REAL NOT NULL DEFAULT 0,
    auto_update_enabled INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_model_updates_user ON user_model_updates(user_id);

-- 8. USER PRIVACY SETTINGS (Privacy preferences)
CREATE TABLE IF NOT EXISTS user_privacy_settings (
    privacy_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    encryption_enabled INTEGER NOT NULL DEFAULT 1,
    data_retention_days INTEGER NOT NULL DEFAULT 90,
    share_anonymous_stats INTEGER NOT NULL DEFAULT 0,
    allow_geolocation INTEGER NOT NULL DEFAULT 1,
    data_deletion_scheduled INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_privacy_settings_user ON user_privacy_settings(user_id);

-- Enable optimizations
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 30000000000;

SELECT '✅ Complete SQLite database schema created!' AS status;

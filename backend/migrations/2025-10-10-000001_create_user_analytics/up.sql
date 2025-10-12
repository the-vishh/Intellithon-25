-- 📊 USER ANALYTICS TABLES - UP MIGRATION
-- Personal analytics with end-to-end encryption

-- 1. USER ACTIVITY (Real-time activity feed)
CREATE TABLE user_activity (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    encrypted_url TEXT NOT NULL,
    url_hash VARCHAR(64) NOT NULL,
    encrypted_domain VARCHAR(500) NOT NULL,
    domain_hash VARCHAR(64) NOT NULL,
    is_phishing BOOLEAN NOT NULL DEFAULT FALSE,
    threat_type VARCHAR(50),
    threat_level VARCHAR(20) NOT NULL DEFAULT 'unknown',
    confidence FLOAT8,
    action_taken VARCHAR(20) NOT NULL DEFAULT 'allowed',
    user_override BOOLEAN NOT NULL DEFAULT FALSE,
    encryption_nonce VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_activity_user_timestamp ON user_activity(user_id, timestamp DESC);
CREATE INDEX idx_user_activity_url_hash ON user_activity(url_hash);
CREATE INDEX idx_user_activity_domain_hash ON user_activity(domain_hash);

-- 2. DEVICE METRICS (Performance tracking)
CREATE TABLE device_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_fingerprint VARCHAR(100) NOT NULL,
    browser VARCHAR(50),
    os VARCHAR(50),
    processing_speed_ms FLOAT8 NOT NULL DEFAULT 0,
    memory_usage_mb FLOAT8 NOT NULL DEFAULT 0,
    cache_hit_rate FLOAT8 NOT NULL DEFAULT 0,
    local_db_size_mb FLOAT8 NOT NULL DEFAULT 0,
    pending_scans INT NOT NULL DEFAULT 0,
    failed_scans INT NOT NULL DEFAULT 0,
    meets_performance_target BOOLEAN NOT NULL DEFAULT TRUE,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_device_metrics_user ON device_metrics(user_id);
CREATE INDEX idx_device_metrics_fingerprint ON device_metrics(device_fingerprint);

-- 3. USER THREAT STATS (Threat breakdown)
CREATE TABLE user_threat_stats (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    phishing_count INT NOT NULL DEFAULT 0,
    malware_count INT NOT NULL DEFAULT 0,
    cryptojacking_count INT NOT NULL DEFAULT 0,
    ransomware_count INT NOT NULL DEFAULT 0,
    scam_count INT NOT NULL DEFAULT 0,
    data_harvesting_count INT NOT NULL DEFAULT 0,
    critical_threats INT NOT NULL DEFAULT 0,
    high_threats INT NOT NULL DEFAULT 0,
    medium_threats INT NOT NULL DEFAULT 0,
    low_threats INT NOT NULL DEFAULT 0,
    total_blocked INT NOT NULL DEFAULT 0,
    total_warnings INT NOT NULL DEFAULT 0,
    total_allowed INT NOT NULL DEFAULT 0,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_threat_stats_user ON user_threat_stats(user_id);

-- 4. USER THREAT SOURCES (Geographic origins)
CREATE TABLE user_threat_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    country_code VARCHAR(2),
    country_name VARCHAR(100),
    threat_count INT NOT NULL DEFAULT 1,
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_threat_sources_user ON user_threat_sources(user_id);
CREATE INDEX idx_user_threat_sources_country ON user_threat_sources(country_code);

-- 5. USER SCAN QUEUE (Queue status)
CREATE TABLE user_scan_queue (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pending_count INT NOT NULL DEFAULT 0,
    processing_count INT NOT NULL DEFAULT 0,
    failed_count INT NOT NULL DEFAULT 0,
    avg_wait_time_ms FLOAT8 NOT NULL DEFAULT 0,
    oldest_pending_timestamp TIMESTAMPTZ,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_scan_queue_user ON user_scan_queue(user_id);

-- 6. USER MODEL UPDATES (Model version tracking)
CREATE TABLE user_model_updates (
    update_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    current_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    update_available BOOLEAN NOT NULL DEFAULT FALSE,
    new_version VARCHAR(20),
    model_size_mb FLOAT8 NOT NULL DEFAULT 0,
    auto_update_enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_user_model_updates_user ON user_model_updates(user_id);

-- 7. USER PRIVACY SETTINGS (Privacy preferences)
CREATE TABLE user_privacy_settings (
    privacy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    encryption_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    data_retention_days INT NOT NULL DEFAULT 90,
    share_anonymous_stats BOOLEAN NOT NULL DEFAULT FALSE,
    allow_geolocation BOOLEAN NOT NULL DEFAULT TRUE,
    data_deletion_scheduled TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_privacy_settings_user ON user_privacy_settings(user_id);

-- Insert default privacy settings for existing users
INSERT INTO user_privacy_settings (user_id)
SELECT user_id FROM users
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ User analytics tables created successfully!';
END $$;

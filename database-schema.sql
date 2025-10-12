-- ============================================================================
-- PHISHGUARD AI - POSTGRESQL DATABASE SCHEMA
-- ============================================================================
-- Multi-user production database for storing scans, statistics, and metrics
-- ============================================================================

-- Drop existing tables if they exist (for fresh start)
DROP TABLE IF EXISTS scans CASCADE;
DROP TABLE IF EXISTS model_metrics CASCADE;
DROP TABLE IF EXISTS global_stats CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- TABLE: users
-- ============================================================================
-- Stores user information for multi-user support
-- Each browser extension instance gets a unique user_id (UUID)

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extension_version VARCHAR(20),
    browser_type VARCHAR(50),  -- chrome, firefox, edge
    total_scans INTEGER DEFAULT 0,
    threats_blocked INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}'::jsonb  -- Store user preferences (sensitivity mode, etc.)
);

-- Index for active user queries
CREATE INDEX idx_users_active ON users(is_active, last_active DESC);
CREATE INDEX idx_users_created ON users(created_at DESC);

-- ============================================================================
-- TABLE: scans
-- ============================================================================
-- Stores every URL scan with full details
-- This is the primary data table for analytics and statistics

CREATE TABLE scans (
    scan_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    domain VARCHAR(255),
    is_phishing BOOLEAN NOT NULL,
    confidence NUMERIC(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    threat_level VARCHAR(20) NOT NULL,  -- SAFE, LOW, MEDIUM, HIGH, CRITICAL
    sensitivity_mode VARCHAR(20) NOT NULL DEFAULT 'balanced',  -- conservative, balanced, aggressive
    threshold_used NUMERIC(5, 4) NOT NULL,
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    latency_ms NUMERIC(8, 2),
    feature_extraction_ms NUMERIC(8, 2),
    ml_inference_ms NUMERIC(8, 2),
    model_version VARCHAR(20),
    cached BOOLEAN DEFAULT FALSE,
    blocked BOOLEAN DEFAULT FALSE,  -- Whether user was actually blocked
    user_override BOOLEAN DEFAULT FALSE,  -- If user clicked "proceed anyway"
    details JSONB  -- Additional metadata
);

-- Indexes for common queries
CREATE INDEX idx_scans_user_id ON scans(user_id, scanned_at DESC);
CREATE INDEX idx_scans_timestamp ON scans(scanned_at DESC);
CREATE INDEX idx_scans_is_phishing ON scans(is_phishing);
CREATE INDEX idx_scans_domain ON scans(domain);
CREATE INDEX idx_scans_threat_level ON scans(threat_level);
CREATE INDEX idx_scans_sensitivity ON scans(sensitivity_mode);

-- Index for performance analysis
CREATE INDEX idx_scans_latency ON scans(latency_ms) WHERE latency_ms IS NOT NULL;

-- ============================================================================
-- TABLE: model_metrics
-- ============================================================================
-- Stores ML model performance metrics calculated hourly
-- Used to track model accuracy, precision, recall, etc.

CREATE TABLE model_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    time_window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    time_window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    model_version VARCHAR(20) NOT NULL,

    -- Performance metrics
    total_predictions INTEGER NOT NULL,
    true_positives INTEGER NOT NULL DEFAULT 0,
    true_negatives INTEGER NOT NULL DEFAULT 0,
    false_positives INTEGER NOT NULL DEFAULT 0,
    false_negatives INTEGER NOT NULL DEFAULT 0,

    -- Calculated metrics
    accuracy NUMERIC(5, 4),  -- (TP + TN) / Total
    precision NUMERIC(5, 4),  -- TP / (TP + FP)
    recall NUMERIC(5, 4),  -- TP / (TP + FN)
    f1_score NUMERIC(5, 4),  -- 2 * (precision * recall) / (precision + recall)
    false_positive_rate NUMERIC(5, 4),  -- FP / (FP + TN)

    -- Performance metrics
    avg_latency_ms NUMERIC(8, 2),
    median_latency_ms NUMERIC(8, 2),
    p95_latency_ms NUMERIC(8, 2),
    p99_latency_ms NUMERIC(8, 2),
    avg_feature_extraction_ms NUMERIC(8, 2),
    avg_ml_inference_ms NUMERIC(8, 2),

    -- By sensitivity mode
    conservative_predictions INTEGER DEFAULT 0,
    balanced_predictions INTEGER DEFAULT 0,
    aggressive_predictions INTEGER DEFAULT 0,

    details JSONB  -- Additional metrics and metadata
);

-- Index for time-based queries
CREATE INDEX idx_model_metrics_time ON model_metrics(time_window_end DESC);
CREATE INDEX idx_model_metrics_version ON model_metrics(model_version, calculated_at DESC);

-- ============================================================================
-- TABLE: global_stats
-- ============================================================================
-- Pre-aggregated statistics for fast dashboard queries
-- Updated in real-time using Redis, persisted hourly to PostgreSQL

CREATE TABLE global_stats (
    stat_id BIGSERIAL PRIMARY KEY,
    snapshot_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    time_period VARCHAR(20) NOT NULL,  -- hourly, daily, weekly, monthly, all_time

    -- User statistics
    total_users INTEGER NOT NULL DEFAULT 0,
    active_users_24h INTEGER NOT NULL DEFAULT 0,
    active_users_7d INTEGER NOT NULL DEFAULT 0,
    new_users_today INTEGER NOT NULL DEFAULT 0,

    -- Scan statistics
    total_scans BIGINT NOT NULL DEFAULT 0,
    scans_24h INTEGER NOT NULL DEFAULT 0,
    scans_7d INTEGER NOT NULL DEFAULT 0,

    -- Threat statistics
    threats_blocked BIGINT NOT NULL DEFAULT 0,
    threats_blocked_24h INTEGER NOT NULL DEFAULT 0,
    threats_blocked_7d INTEGER NOT NULL DEFAULT 0,

    -- By threat level
    critical_threats INTEGER NOT NULL DEFAULT 0,
    high_threats INTEGER NOT NULL DEFAULT 0,
    medium_threats INTEGER NOT NULL DEFAULT 0,
    low_threats INTEGER NOT NULL DEFAULT 0,
    safe_urls INTEGER NOT NULL DEFAULT 0,

    -- By sensitivity mode
    conservative_scans INTEGER NOT NULL DEFAULT 0,
    balanced_scans INTEGER NOT NULL DEFAULT 0,
    aggressive_scans INTEGER NOT NULL DEFAULT 0,

    -- Performance
    avg_latency_ms NUMERIC(8, 2),
    cache_hit_rate NUMERIC(5, 4),

    -- Top domains
    top_blocked_domains JSONB,  -- [{domain, count}, ...]
    top_safe_domains JSONB,

    details JSONB  -- Additional statistics
);

-- Index for time-based queries
CREATE INDEX idx_global_stats_time ON global_stats(time_period, snapshot_at DESC);

-- ============================================================================
-- FUNCTIONS: Update Triggers
-- ============================================================================

-- Function to update user last_active timestamp
CREATE OR REPLACE FUNCTION update_user_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users
    SET last_active = NOW(),
        total_scans = total_scans + 1,
        threats_blocked = threats_blocked + CASE WHEN NEW.is_phishing THEN 1 ELSE 0 END
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update user stats on new scan
CREATE TRIGGER trigger_update_user_stats
AFTER INSERT ON scans
FOR EACH ROW
EXECUTE FUNCTION update_user_last_active();

-- ============================================================================
-- VIEWS: Pre-computed Views for Common Queries
-- ============================================================================

-- View: Recent scans with user info
CREATE OR REPLACE VIEW recent_scans AS
SELECT
    s.scan_id,
    s.user_id,
    s.url,
    s.domain,
    s.is_phishing,
    s.confidence,
    s.threat_level,
    s.sensitivity_mode,
    s.threshold_used,
    s.scanned_at,
    s.latency_ms,
    u.browser_type,
    u.extension_version
FROM scans s
JOIN users u ON s.user_id = u.user_id
ORDER BY s.scanned_at DESC
LIMIT 1000;

-- View: Threat statistics by domain
CREATE OR REPLACE VIEW domain_threat_stats AS
SELECT
    domain,
    COUNT(*) as total_scans,
    COUNT(*) FILTER (WHERE is_phishing) as threat_count,
    AVG(confidence) as avg_confidence,
    MAX(scanned_at) as last_seen,
    COUNT(DISTINCT user_id) as unique_users
FROM scans
WHERE domain IS NOT NULL
GROUP BY domain
ORDER BY threat_count DESC;

-- View: User statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT
    u.user_id,
    u.created_at,
    u.last_active,
    u.browser_type,
    u.total_scans,
    u.threats_blocked,
    COALESCE(recent_scans.scans_24h, 0) as scans_24h,
    COALESCE(recent_threats.threats_24h, 0) as threats_blocked_24h
FROM users u
LEFT JOIN (
    SELECT user_id, COUNT(*) as scans_24h
    FROM scans
    WHERE scanned_at > NOW() - INTERVAL '24 hours'
    GROUP BY user_id
) recent_scans ON u.user_id = recent_scans.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as threats_24h
    FROM scans
    WHERE scanned_at > NOW() - INTERVAL '24 hours' AND is_phishing = true
    GROUP BY user_id
) recent_threats ON u.user_id = recent_threats.user_id;

-- View: Performance metrics by sensitivity mode
CREATE OR REPLACE VIEW sensitivity_performance AS
SELECT
    sensitivity_mode,
    COUNT(*) as total_scans,
    COUNT(*) FILTER (WHERE is_phishing) as threats_detected,
    ROUND(AVG(confidence), 4) as avg_confidence,
    ROUND(AVG(latency_ms), 2) as avg_latency_ms,
    ROUND(AVG(threshold_used), 2) as avg_threshold,
    COUNT(DISTINCT user_id) as unique_users
FROM scans
GROUP BY sensitivity_mode
ORDER BY sensitivity_mode;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get global statistics (last 24 hours)
/*
SELECT
    COUNT(DISTINCT user_id) as active_users,
    COUNT(*) as total_scans,
    COUNT(*) FILTER (WHERE is_phishing) as threats_blocked,
    ROUND(AVG(confidence), 3) as avg_confidence,
    ROUND(AVG(latency_ms), 2) as avg_latency_ms,
    COUNT(*) FILTER (WHERE sensitivity_mode = 'conservative') as conservative_users,
    COUNT(*) FILTER (WHERE sensitivity_mode = 'balanced') as balanced_users,
    COUNT(*) FILTER (WHERE sensitivity_mode = 'aggressive') as aggressive_users
FROM scans
WHERE scanned_at > NOW() - INTERVAL '24 hours';
*/

-- Get user-specific statistics
/*
SELECT
    COUNT(*) as total_scans,
    COUNT(*) FILTER (WHERE is_phishing) as threats_blocked,
    COUNT(*) FILTER (WHERE threat_level = 'CRITICAL') as critical_threats,
    ROUND(AVG(confidence), 3) as avg_confidence,
    MAX(scanned_at) as last_scan
FROM scans
WHERE user_id = 'USER_UUID_HERE';
*/

-- Get top blocked domains
/*
SELECT
    domain,
    COUNT(*) as block_count,
    AVG(confidence) as avg_confidence,
    MAX(scanned_at) as last_blocked
FROM scans
WHERE is_phishing = true AND domain IS NOT NULL
GROUP BY domain
ORDER BY block_count DESC
LIMIT 10;
*/

-- Get model performance over time
/*
SELECT
    time_window_end::date as date,
    AVG(accuracy) as avg_accuracy,
    AVG(precision) as avg_precision,
    AVG(recall) as avg_recall,
    AVG(f1_score) as avg_f1_score,
    AVG(avg_latency_ms) as avg_latency
FROM model_metrics
WHERE time_window_end > NOW() - INTERVAL '7 days'
GROUP BY date
ORDER BY date DESC;
*/

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert initial global_stats row
INSERT INTO global_stats (time_period) VALUES ('all_time');

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO phishguard_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO phishguard_app;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

COMMENT ON TABLE users IS 'Stores user information for multi-user support';
COMMENT ON TABLE scans IS 'Stores every URL scan with full details for analytics';
COMMENT ON TABLE model_metrics IS 'Stores ML model performance metrics calculated hourly';
COMMENT ON TABLE global_stats IS 'Pre-aggregated statistics for fast dashboard queries';

-- Display table information
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Success message
\echo '✅ PhishGuard AI database schema created successfully!'
\echo ''
\echo '📊 Tables created:'
\echo '   • users - User accounts and preferences'
\echo '   • scans - All URL scans with full details'
\echo '   • model_metrics - ML model performance metrics'
\echo '   • global_stats - Pre-aggregated statistics'
\echo ''
\echo '📈 Views created:'
\echo '   • recent_scans - Recent scans with user info'
\echo '   • domain_threat_stats - Threat statistics by domain'
\echo '   • user_stats - User statistics and activity'
\echo '   • sensitivity_performance - Performance by sensitivity mode'
\echo ''
\echo '🚀 Next steps:'
\echo '   1. Update Rust backend to connect to PostgreSQL'
\echo '   2. Log all scans to database'
\echo '   3. Create API endpoints for global statistics'
\echo '   4. Build web dashboard to display data'

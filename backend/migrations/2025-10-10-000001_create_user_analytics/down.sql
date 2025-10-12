-- 📊 USER ANALYTICS TABLES - DOWN MIGRATION
-- Rollback script to drop all analytics tables

DROP TABLE IF EXISTS user_privacy_settings CASCADE;
DROP TABLE IF EXISTS user_model_updates CASCADE;
DROP TABLE IF EXISTS user_scan_queue CASCADE;
DROP TABLE IF EXISTS user_threat_sources CASCADE;
DROP TABLE IF EXISTS user_threat_stats CASCADE;
DROP TABLE IF EXISTS device_metrics CASCADE;
DROP TABLE IF EXISTS user_activity CASCADE;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ User analytics tables dropped successfully!';
END $$;

// @generated automatically for SQLite
// PhishGuard Database Schema

diesel::table! {
    users (user_id) {
        user_id -> Text,
        extension_id -> Text,
        email -> Nullable<Text>,
        username -> Nullable<Text>,
        sensitivity_mode -> Text,
        protection_enabled -> Integer,
        ai_detection_enabled -> Integer,
        subscription_tier -> Text,
        subscription_expires_at -> Nullable<Integer>,
        created_at -> Integer,
        last_active_at -> Integer,
        total_scans -> Integer,
        total_threats_blocked -> Integer,
        average_response_time_ms -> Double,
        is_active -> Integer,
        is_banned -> Integer,
        ban_reason -> Nullable<Text>,
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
        timestamp -> BigInt,  // Changed to BigInt for i64
    }
}

diesel::table! {
    device_metrics (metric_id) {
        metric_id -> Text,
        user_id -> Text,
        device_fingerprint -> Text,
        browser -> Nullable<Text>,
        browser_version -> Nullable<Text>,
        os -> Nullable<Text>,
        extension_version -> Nullable<Text>,
        avg_processing_speed_ms -> Nullable<Double>,
        memory_usage_mb -> Nullable<Double>,
        cache_hit_rate -> Nullable<Double>,
        feature_extraction_ms -> Nullable<Double>,
        ml_inference_ms -> Nullable<Double>,
        network_latency_ms -> Nullable<Double>,
        local_db_size_mb -> Nullable<Double>,
        cache_entries -> Nullable<Integer>,
        last_cache_clear -> Nullable<Integer>,
        pending_scans -> Nullable<Integer>,
        failed_scans -> Nullable<Integer>,
        model_version -> Nullable<Text>,
        model_last_updated -> Nullable<Integer>,
        model_size_mb -> Nullable<Double>,
        first_seen -> Integer,
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
        period_start -> Nullable<BigInt>,  // Changed to BigInt for i64
        period_end -> Nullable<BigInt>,    // Changed to BigInt for i64
        created_at -> BigInt,               // Changed to BigInt for i64
        updated_at -> BigInt,               // Changed to BigInt for i64
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
        last_seen -> BigInt,  // Changed to BigInt for i64
        created_at -> BigInt,  // Changed to BigInt for i64
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

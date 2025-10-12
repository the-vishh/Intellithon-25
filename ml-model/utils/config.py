"""
Configuration file for Elite Phishing Detection ML Model
"""

import os
from pathlib import Path

# ============================================================================
# DIRECTORY PATHS
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    EXTERNAL_DATA_DIR,
    MODELS_DIR,
    LOGS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATA COLLECTION
# ============================================================================
DATA_SOURCES = {
    "phishtank": {
        "url": "http://data.phishtank.com/data/online-valid.csv",
        "format": "csv",
        "update_frequency": "hourly",
    },
    "openphish": {
        "url": "https://openphish.com/feed.txt",
        "format": "txt",
        "update_frequency": "hourly",
    },
    "alexa": {
        "url": "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip",
        "format": "csv",
        "sample_size": 10000,
    },
}

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================
FEATURE_CONFIG = {
    "url_features": {"enabled": True, "count": 30, "timeout": 5},  # seconds
    "ssl_features": {"enabled": True, "count": 20, "timeout": 10},
    "dns_features": {"enabled": True, "count": 15, "timeout": 10},
    "subdomain_features": {"enabled": True, "count": 12, "timeout": 5},
    "content_features": {"enabled": True, "count": 40, "timeout": 15},
    "js_features": {"enabled": True, "count": 25, "timeout": 10},
    "visual_features": {"enabled": True, "count": 18, "timeout": 20},
}

TOTAL_FEATURES = sum(f["count"] for f in FEATURE_CONFIG.values() if f["enabled"])

# ============================================================================
# MODEL HYPERPARAMETERS
# ============================================================================
RANDOM_FOREST_PARAMS = {
    "n_estimators": 500,
    "max_depth": 20,
    "min_samples_split": 10,
    "min_samples_leaf": 4,
    "max_features": "sqrt",
    "bootstrap": True,
    "n_jobs": -1,
    "random_state": 42,
    "class_weight": "balanced",
}

XGBOOST_PARAMS = {
    "n_estimators": 500,
    "max_depth": 10,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "gamma": 0.1,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "n_jobs": -1,
    "random_state": 42,
    "tree_method": "hist",
}

LIGHTGBM_PARAMS = {
    "n_estimators": 500,
    "max_depth": 10,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "reg_alpha": 0.1,
    "reg_lambda": 1.0,
    "objective": "binary",
    "metric": "auc",
    "n_jobs": -1,
    "random_state": 42,
    "verbose": -1,
}

LSTM_PARAMS = {
    "embedding_dim": 128,
    "lstm_units": [128, 64],
    "dropout": 0.3,
    "recurrent_dropout": 0.3,
    "dense_units": [64, 32],
    "activation": "relu",
    "optimizer": "adam",
    "learning_rate": 0.001,
    "batch_size": 64,
    "epochs": 50,
    "early_stopping_patience": 10,
}

CNN_PARAMS = {
    "conv_filters": [32, 64, 128],
    "kernel_sizes": [3, 3, 3],
    "pool_sizes": [2, 2, 2],
    "dropout": 0.3,
    "dense_units": [128, 64],
    "activation": "relu",
    "optimizer": "adam",
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 50,
}

# ============================================================================
# ENSEMBLE CONFIGURATION
# ============================================================================
ENSEMBLE_WEIGHTS = {
    "random_forest": 0.25,
    "xgboost": 0.30,
    "lightgbm": 0.25,
    "lstm": 0.20,
}

CLASSIFICATION_THRESHOLDS = {
    "phishing": 0.3,  # Score < 0.3 = Phishing
    "safe": 0.7,  # Score > 0.7 = Safe
    # Between 0.3-0.7 = Suspicious
}

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================
TRAIN_CONFIG = {
    "test_size": 0.15,
    "val_size": 0.15,
    "random_state": 42,
    "stratify": True,
    "cross_validation_folds": 5,
}

# ============================================================================
# PERFORMANCE TARGETS
# ============================================================================
PERFORMANCE_TARGETS = {
    "accuracy": 0.98,  # >98%
    "false_positive_rate": 0.005,  # <0.5%
    "inference_time_ms": 10,  # <10ms
    "feature_extraction_ms": 50,  # <50ms
    "total_latency_ms": 100,  # <100ms
}

# ============================================================================
# API KEYS (SET AS ENVIRONMENT VARIABLES)
# ============================================================================
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")

# ============================================================================
# THREAT INTELLIGENCE
# ============================================================================
THREAT_INTEL_CONFIG = {
    "cache_ttl": 3600,  # 1 hour
    "update_interval": 3600,
    "sources": ["phishtank", "openphish", "virustotal", "google_safe_browsing"],
}

# ============================================================================
# URL ANALYSIS THRESHOLDS
# ============================================================================
URL_THRESHOLDS = {
    "max_length": 75,
    "max_subdomains": 3,
    "suspicious_keywords": [
        "login",
        "verify",
        "account",
        "update",
        "secure",
        "banking",
        "confirm",
        "suspended",
        "locked",
        "urgent",
        "expire",
    ],
    "suspicious_tlds": [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".online"],
}

# ============================================================================
# SSL/TLS CONFIGURATION
# ============================================================================
SSL_CONFIG = {
    "min_certificate_age_days": 30,
    "trusted_ca_list": [
        "Let's Encrypt",
        "DigiCert",
        "Comodo",
        "GeoTrust",
        "Thawte",
        "RapidSSL",
        "GlobalSign",
        "Entrust",
    ],
    "check_certificate_transparency": True,
}

# ============================================================================
# DNS CONFIGURATION
# ============================================================================
DNS_CONFIG = {
    "min_domain_age_days": 180,  # 6 months
    "trusted_registrars": [
        "GoDaddy",
        "Namecheap",
        "Google Domains",
        "CloudFlare",
        "Amazon Registrar",
        "MarkMonitor",
    ],
    "dns_servers": [
        "8.8.8.8",  # Google
        "1.1.1.1",  # Cloudflare
        "208.67.222.222",  # OpenDNS
    ],
}

# ============================================================================
# CONTENT ANALYSIS
# ============================================================================
CONTENT_CONFIG = {
    "urgency_keywords": [
        "act now",
        "limited time",
        "expire",
        "suspended",
        "verify",
        "click here",
        "confirm",
        "urgent",
        "immediate",
        "security alert",
    ],
    "suspicious_form_fields": [
        "password",
        "credit_card",
        "cvv",
        "ssn",
        "pin",
        "account_number",
    ],
    "max_external_links_ratio": 0.7,
}

# ============================================================================
# JAVASCRIPT ANALYSIS
# ============================================================================
JS_CONFIG = {
    "suspicious_apis": [
        "eval",
        "document.cookie",
        "localStorage",
        "sessionStorage",
        "window.open",
        "document.write",
        "innerHTML",
    ],
    "obfuscation_patterns": [
        "eval",
        "unescape",
        "fromCharCode",
        "atob",
        "btoa",
        "String.fromCharCode",
        "decodeURIComponent",
    ],
    "max_script_size_kb": 500,
}

# ============================================================================
# VISUAL ANALYSIS
# ============================================================================
VISUAL_CONFIG = {
    "logo_similarity_threshold": 0.85,
    "perceptual_hash_size": 8,
    "brand_logo_database": EXTERNAL_DATA_DIR / "brand_logos",
    "screenshot_width": 1920,
    "screenshot_height": 1080,
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "ml_model.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "standard",
            "level": "DEBUG",
        },
    },
    "loggers": {"": {"handlers": ["console", "file"], "level": "INFO"}},
}

# ============================================================================
# MODEL EXPORT CONFIGURATION
# ============================================================================
EXPORT_CONFIG = {
    "tensorflowjs": {
        "quantization": "uint8",  # INT8 quantization
        "output_format": "tfjs_layers_model",
    },
    "onnx": {"opset_version": 13, "optimize": True},
}

# ============================================================================
# BENCHMARKING
# ============================================================================
BENCHMARK_CONFIG = {
    "iterations": 10000,
    "warmup_iterations": 100,
    "parallel_requests": 10,
}

print(f" Configuration loaded successfully!")
print(f" Total Features: {TOTAL_FEATURES}")
print(
    f" Performance Targets: {PERFORMANCE_TARGETS['accuracy']*100}% accuracy, <{PERFORMANCE_TARGETS['total_latency_ms']}ms latency"
)

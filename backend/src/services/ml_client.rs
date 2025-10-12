/*!
 * HTTP client for Python ML service
 */

use reqwest::Client;
use anyhow::Result;
use serde::{Deserialize, Serialize};

use crate::models::URLCheckResponse;

/// HTTP client for ML service
pub struct MLClient {
    client: Client,
    base_url: String,
}

#[derive(Debug, Serialize)]
struct MLRequest {
    url: String,
    sensitivity_mode: String,
}

#[derive(Debug, Deserialize)]
struct MLResponse {
    url: String,
    is_phishing: bool,
    confidence: f64,
    threat_level: String,
    sensitivity_mode: String,
    threshold_used: f64,
    details: serde_json::Value,
    latency_ms: f64,
    model_version: String,
    performance_metrics: serde_json::Value,
}

impl MLClient {
    /// Create new ML client
    pub fn new(base_url: &str) -> Self {
        Self {
            client: Client::new(),
            base_url: base_url.to_string(),
        }
    }

    /// Predict if URL is phishing
    pub async fn predict(&self, url: &str, sensitivity_mode: &str) -> Result<URLCheckResponse> {
        let endpoint = format!("{}/api/predict", self.base_url);

        log::debug!("📊 Calling ML service: {} (mode: {})", url, sensitivity_mode);
        let start = std::time::Instant::now();

        let response = self.client
            .post(&endpoint)
            .json(&MLRequest {
                url: url.to_string(),
                sensitivity_mode: sensitivity_mode.to_string(),
            })
            .timeout(std::time::Duration::from_secs(10))
            .send()
            .await?;

        let elapsed = start.elapsed();
        log::debug!("⏱️  ML service responded in {:?}", elapsed);

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            anyhow::bail!("ML service error {}: {}", status, error_text);
        }

        let ml_response: MLResponse = response.json().await?;

        Ok(URLCheckResponse {
            url: ml_response.url,
            is_phishing: ml_response.is_phishing,
            confidence: ml_response.confidence,
            threat_level: ml_response.threat_level,
            sensitivity_mode: ml_response.sensitivity_mode,
            threshold_used: ml_response.threshold_used,
            details: ml_response.details,
            latency_ms: ml_response.latency_ms,
            cached: false,
            timestamp: chrono::Utc::now(),
            performance_metrics: ml_response.performance_metrics,
            model_version: ml_response.model_version,
        })
    }

    /// Health check for ML service
    pub async fn health_check(&self) -> Result<bool> {
        let endpoint = format!("{}/health", self.base_url);

        let response = self.client
            .get(&endpoint)
            .timeout(std::time::Duration::from_secs(5))
            .send()
            .await?;

        Ok(response.status().is_success())
    }
}

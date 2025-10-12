"""
 PHISHGUARD AI - EXPLAINABLE AI MODULE
========================================

Provides human-interpretable explanations for ML predictions using SHAP

Features:
- SHAP (SHapley Additive exPlanations) integration
- Feature importance calculation
- Human-readable explanation generation
- Explanation caching for performance
- Support for ensemble models

Author: PhishGuard AI Team
Version: 2.0.0
Date: October 10, 2025
"""

import numpy as np
import pandas as pd
import shap
import pickle
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExplainableAI:
    """
    Provides explainable AI capabilities for phishing detection models

    Uses SHAP (SHapley Additive exPlanations) to generate feature importance
    and human-readable explanations for predictions.
    """

    def __init__(
        self,
        model_path: str,
        feature_names: List[str],
        cache_size: int = 1000,
        cache_ttl_hours: int = 24,
    ):
        """
        Initialize Explainable AI system

        Args:
            model_path: Path to trained model file
            feature_names: List of feature names (159 features)
            cache_size: Maximum number of cached explanations
            cache_ttl_hours: Time-to-live for cached explanations
        """
        self.model_path = Path(model_path)
        self.feature_names = feature_names
        self.cache_size = cache_size
        self.cache_ttl_hours = cache_ttl_hours

        # Load model
        self.model = self._load_model()

        # Initialize SHAP explainer
        self.explainer = None
        self.background_data = None

        # Explanation cache: {url_hash: (explanation, timestamp)}
        self.explanation_cache: OrderedDict = OrderedDict()

        # Feature category mapping
        self.feature_categories = self._initialize_feature_categories()

        logger.info(f" ExplainableAI initialized with model: {self.model_path.name}")

    def _load_model(self):
        """Load trained ML model"""
        try:
            with open(self.model_path, "rb") as f:
                model = pickle.load(f)
            logger.info(f" Model loaded: {self.model_path.name}")
            return model
        except Exception as e:
            logger.error(f" Failed to load model: {e}")
            raise

    def _initialize_feature_categories(self) -> Dict[str, List[str]]:
        """
        Categorize features for better explanations

        Returns:
            Dictionary mapping category names to feature name patterns
        """
        return {
            "URL Structure": [
                "url_length",
                "hostname_length",
                "path_length",
                "num_dots",
                "num_hyphens",
                "num_underscores",
                "num_slashes",
                "num_digits",
                "num_params",
                "has_ip",
                "has_port",
                "url_entropy",
            ],
            "Domain Security": [
                "domain_age_days",
                "ssl_validity",
                "domain_in_brand",
                "typosquatting_",
                "homograph_attack",
                "subdomain_level",
                "is_https",
                "https_token",
                "suspicious_tld",
            ],
            "Content Analysis": [
                "num_external_links",
                "num_forms",
                "num_iframes",
                "title_",
                "has_password_field",
                "has_hidden_",
                "suspicious_keywords_",
                "brand_impersonation",
            ],
            "URL Patterns": [
                "has_@",
                "has_double_slash",
                "url_shortening",
                "obfuscation_",
                "redirect_",
                "encoded_url",
                "suspicious_file_extension",
            ],
            "Technical Indicators": [
                "dns_record",
                "whois_",
                "page_rank",
                "alexa_rank",
                "google_index",
                "asn_",
                "ptr_record",
            ],
            "Behavioral Signals": [
                "redirect_count",
                "popup_count",
                "login_form",
                "external_favicon",
                "null_links_ratio",
                "abnormal_",
            ],
            "Threat Intelligence": [
                "phishtank_",
                "virustotal_",
                "google_safebrowsing",
                "reputation_score",
                "blacklist_",
                "similarity_",
            ],
        }

    def initialize_explainer(self, background_data: np.ndarray, max_samples: int = 100):
        """
        Initialize SHAP explainer with background data

        Args:
            background_data: Background dataset for SHAP (training data sample)
            max_samples: Maximum samples to use for background
        """
        try:
            # Sample background data if too large
            if len(background_data) > max_samples:
                np.random.seed(42)
                indices = np.random.choice(
                    len(background_data), max_samples, replace=False
                )
                background_data = background_data[indices]

            self.background_data = background_data

            # Create SHAP explainer (TreeExplainer for tree-based models)
            if hasattr(self.model, "predict_proba"):
                # For Random Forest, XGBoost, LightGBM
                self.explainer = shap.TreeExplainer(
                    self.model,
                    data=self.background_data,
                    feature_names=self.feature_names,
                )
                logger.info(" SHAP TreeExplainer initialized")
            else:
                # Fallback to KernelExplainer
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    self.background_data,
                    feature_names=self.feature_names,
                )
                logger.info(" SHAP KernelExplainer initialized")

        except Exception as e:
            logger.error(f" Failed to initialize SHAP explainer: {e}")
            raise

    def explain_prediction(
        self, features: np.ndarray, url: str, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate explanation for a single prediction

        Args:
            features: Feature vector (159 features)
            url: URL being analyzed
            use_cache: Whether to use cached explanations

        Returns:
            Dictionary with explanation details
        """
        # Check cache
        url_hash = self._hash_url(url)
        if use_cache and url_hash in self.explanation_cache:
            cached_explanation, timestamp = self.explanation_cache[url_hash]

            # Check if cache is still valid
            if datetime.now() - timestamp < timedelta(hours=self.cache_ttl_hours):
                logger.info(f" Using cached explanation for {url}")
                return cached_explanation
            else:
                # Remove expired cache entry
                del self.explanation_cache[url_hash]

        # Ensure explainer is initialized
        if self.explainer is None:
            raise ValueError(
                "SHAP explainer not initialized. Call initialize_explainer() first."
            )

        try:
            # Get prediction
            if hasattr(self.model, "predict_proba"):
                prediction_proba = self.model.predict_proba(features.reshape(1, -1))[0]
                prediction = np.argmax(prediction_proba)
                confidence = prediction_proba[prediction]
            else:
                prediction = self.model.predict(features.reshape(1, -1))[0]
                confidence = 1.0

            # Get SHAP values
            shap_values = self.explainer.shap_values(features.reshape(1, -1))

            # Handle multi-class output
            if isinstance(shap_values, list):
                # Use SHAP values for the predicted class
                shap_values = shap_values[prediction]

            # Flatten if needed
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]

            # Get top contributing features
            top_features = self._get_top_features(shap_values, features, top_k=10)

            # Categorize features
            categorized_features = self._categorize_features(top_features)

            # Generate human-readable explanation
            explanation_text = self._generate_explanation_text(
                prediction, confidence, categorized_features
            )

            # Create explanation object
            explanation = {
                "url": url,
                "prediction": "PHISHING" if prediction == 1 else "LEGITIMATE",
                "confidence": float(confidence),
                "risk_score": (
                    float(confidence * 100)
                    if prediction == 1
                    else float((1 - confidence) * 100)
                ),
                "top_features": top_features,
                "categorized_features": categorized_features,
                "explanation_text": explanation_text,
                "shap_values": shap_values.tolist(),
                "base_value": (
                    float(self.explainer.expected_value)
                    if hasattr(self.explainer, "expected_value")
                    else 0.5
                ),
                "timestamp": datetime.now().isoformat(),
            }

            # Cache explanation
            if use_cache:
                self._cache_explanation(url_hash, explanation)

            logger.info(
                f" Generated explanation for {url} - {explanation['prediction']} ({confidence:.2%})"
            )
            return explanation

        except Exception as e:
            logger.error(f" Failed to generate explanation: {e}")
            raise

    def _get_top_features(
        self, shap_values: np.ndarray, features: np.ndarray, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top contributing features by absolute SHAP value

        Args:
            shap_values: SHAP values for each feature
            features: Feature values
            top_k: Number of top features to return

        Returns:
            List of feature dictionaries with names, values, and SHAP values
        """
        # Get absolute SHAP values for sorting
        abs_shap_values = np.abs(shap_values)

        # Get top k indices
        top_indices = np.argsort(abs_shap_values)[-top_k:][::-1]

        top_features = []
        for idx in top_indices:
            if abs_shap_values[idx] > 0.001:  # Only include significant features
                top_features.append(
                    {
                        "name": self.feature_names[idx],
                        "value": float(features[idx]),
                        "shap_value": float(shap_values[idx]),
                        "impact": "increases" if shap_values[idx] > 0 else "decreases",
                        "importance": float(abs_shap_values[idx]),
                    }
                )

        return top_features

    def _categorize_features(
        self, top_features: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize features into meaningful groups

        Args:
            top_features: List of top contributing features

        Returns:
            Dictionary mapping categories to features
        """
        categorized = {}

        for feature in top_features:
            feature_name = feature["name"]

            # Find matching category
            category_found = False
            for category, patterns in self.feature_categories.items():
                for pattern in patterns:
                    if pattern in feature_name:
                        if category not in categorized:
                            categorized[category] = []
                        categorized[category].append(feature)
                        category_found = True
                        break
                if category_found:
                    break

            # Add to 'Other' if no category found
            if not category_found:
                if "Other" not in categorized:
                    categorized["Other"] = []
                categorized["Other"].append(feature)

        return categorized

    def _generate_explanation_text(
        self,
        prediction: int,
        confidence: float,
        categorized_features: Dict[str, List[Dict[str, Any]]],
    ) -> str:
        """
        Generate human-readable explanation text

        Args:
            prediction: Model prediction (0=legitimate, 1=phishing)
            confidence: Prediction confidence
            categorized_features: Features grouped by category

        Returns:
            Human-readable explanation string
        """
        if prediction == 1:
            # Phishing explanation
            explanation = f" **This website was identified as PHISHING with {confidence:.1%} confidence.**\n\n"
            explanation += "**Why this site was blocked:**\n\n"

            for category, features in categorized_features.items():
                if features:
                    explanation += f"**{category}:**\n"
                    for feature in features[:3]:  # Top 3 per category
                        explanation += self._feature_to_sentence(feature) + "\n"
                    explanation += "\n"
        else:
            # Legitimate explanation
            explanation = f" **This website appears LEGITIMATE with {confidence:.1%} confidence.**\n\n"
            explanation += "**Factors supporting legitimacy:**\n\n"

            for category, features in categorized_features.items():
                if features:
                    explanation += f"**{category}:**\n"
                    for feature in features[:3]:
                        explanation += self._feature_to_sentence(feature) + "\n"
                    explanation += "\n"

        return explanation

    def _feature_to_sentence(self, feature: Dict[str, Any]) -> str:
        """
        Convert feature to human-readable sentence

        Args:
            feature: Feature dictionary

        Returns:
            Human-readable sentence
        """
        name = feature["name"]
        value = feature["value"]
        impact = feature["impact"]

        # Custom sentences for common features
        sentences = {
            "url_length": f"- URL length ({int(value)} chars) is {'abnormally long' if value > 75 else 'normal'}",
            "domain_age_days": f"- Domain age ({int(value)} days) is {'very new (suspicious)' if value < 30 else 'established'}",
            "has_ip": f"- URL {'contains IP address instead of domain name' if value == 1 else 'uses proper domain name'}",
            "ssl_validity": f"- SSL certificate is {'invalid or missing' if value == 0 else 'valid'}",
            "num_external_links": f"- Page has {int(value)} external links ({'excessive' if value > 20 else 'normal'})",
            "has_password_field": f"- Page {'requests password input' if value == 1 else 'has no password fields'}",
            "phishtank_match": f"- {'Found in PhishTank database' if value == 1 else 'Not in known phishing databases'}",
            "typosquatting_detected": f"- {'Typosquatting detected (similar to known brand)' if value == 1 else 'No typosquatting detected'}",
            "url_entropy": f"- URL randomness score ({value:.2f}) is {'high (obfuscated)' if value > 4 else 'normal'}",
            "num_dots": f"- {int(value)} dots in URL ({'excessive subdomains' if value > 5 else 'normal'})",
            "has_@": f"- URL {'contains @ symbol (credential phishing indicator)' if value == 1 else 'has no suspicious symbols'}",
            "redirect_count": f"- {int(value)} redirects detected ({'suspicious' if value > 2 else 'normal'})",
        }

        # Return custom sentence if available
        if name in sentences:
            return sentences[name]

        # Generic sentence
        if impact == "increases":
            return f"- {name.replace('_', ' ').title()}: {value:.2f} (increases phishing risk)"
        else:
            return f"- {name.replace('_', ' ').title()}: {value:.2f} (decreases phishing risk)"

    def _hash_url(self, url: str) -> str:
        """Generate hash for URL caching"""
        return hashlib.sha256(url.encode()).hexdigest()

    def _cache_explanation(self, url_hash: str, explanation: Dict[str, Any]):
        """
        Cache explanation with LRU eviction

        Args:
            url_hash: Hash of the URL
            explanation: Explanation dictionary to cache
        """
        # Add to cache
        self.explanation_cache[url_hash] = (explanation, datetime.now())

        # Evict oldest if cache is full
        if len(self.explanation_cache) > self.cache_size:
            self.explanation_cache.popitem(last=False)

    def batch_explain(
        self, features_batch: np.ndarray, urls: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate explanations for multiple predictions

        Args:
            features_batch: Batch of feature vectors
            urls: List of URLs

        Returns:
            List of explanation dictionaries
        """
        explanations = []

        for features, url in zip(features_batch, urls):
            try:
                explanation = self.explain_prediction(features, url)
                explanations.append(explanation)
            except Exception as e:
                logger.error(f" Failed to explain {url}: {e}")
                explanations.append(
                    {
                        "url": url,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return explanations

    def export_explanation(
        self, explanation: Dict[str, Any], format: str = "json"
    ) -> str:
        """
        Export explanation in specified format

        Args:
            explanation: Explanation dictionary
            format: Export format ('json', 'html', 'text')

        Returns:
            Formatted explanation string
        """
        if format == "json":
            return json.dumps(explanation, indent=2)

        elif format == "html":
            html = f"""
            <div class="phishguard-explanation">
                <h2>PhishGuard AI Analysis</h2>
                <div class="prediction {explanation['prediction'].lower()}">
                    <strong>Verdict:</strong> {explanation['prediction']}
                    ({explanation['confidence']:.1%} confidence)
                </div>
                <div class="risk-score">
                    <strong>Risk Score:</strong> {explanation['risk_score']:.1f}/100
                </div>
                <div class="explanation-text">
                    {explanation['explanation_text'].replace('\n', '<br>')}
                </div>
                <div class="timestamp">
                    <em>Analysis performed: {explanation['timestamp']}</em>
                </div>
            </div>
            """
            return html

        elif format == "text":
            text = f"""
PhishGuard AI Analysis
{'=' * 50}
URL: {explanation['url']}
Verdict: {explanation['prediction']} ({explanation['confidence']:.1%})
Risk Score: {explanation['risk_score']:.1f}/100

{explanation['explanation_text']}

Analysis performed: {explanation['timestamp']}
            """
            return text.strip()

        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.explanation_cache),
            "max_cache_size": self.cache_size,
            "cache_ttl_hours": self.cache_ttl_hours,
            "cache_utilization": len(self.explanation_cache) / self.cache_size,
        }

    def clear_cache(self):
        """Clear explanation cache"""
        self.explanation_cache.clear()
        logger.info(" Explanation cache cleared")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def create_explainable_ai(
    model_path: str, feature_names_path: str, background_data_path: str
) -> ExplainableAI:
    """
    Factory function to create ExplainableAI instance

    Args:
        model_path: Path to trained model
        feature_names_path: Path to feature names JSON
        background_data_path: Path to background data CSV

    Returns:
        Initialized ExplainableAI instance
    """
    # Load feature names
    with open(feature_names_path, "r") as f:
        feature_names = json.load(f)

    # Create explainer
    explainer = ExplainableAI(model_path=model_path, feature_names=feature_names)

    # Load and initialize background data
    background_data = pd.read_csv(background_data_path).values
    explainer.initialize_explainer(background_data, max_samples=100)

    return explainer


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print(" PhishGuard AI - Explainable AI Module")
    print("=" * 50)

    # This would be replaced with actual paths
    model_path = "../models/random_forest_159features.pkl"
    feature_names = [f"feature_{i}" for i in range(159)]

    # Create mock background data
    background_data = np.random.randn(100, 159)

    try:
        # Initialize explainer
        explainer = ExplainableAI(model_path=model_path, feature_names=feature_names)

        explainer.initialize_explainer(background_data)

        # Test explanation
        test_features = np.random.randn(159)
        test_url = "http://suspicious-site.com/login"

        explanation = explainer.explain_prediction(test_features, test_url)

        print("\n Explanation generated successfully!")
        print(f"Prediction: {explanation['prediction']}")
        print(f"Confidence: {explanation['confidence']:.2%}")
        print(f"\nTop Features:")
        for feature in explanation["top_features"][:5]:
            print(f"  - {feature['name']}: {feature['shap_value']:.4f}")

    except FileNotFoundError:
        print("\n Model file not found (this is expected in testing)")
        print(" Module structure is correct!")

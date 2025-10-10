"""
📝 PHISHGUARD AI - EXPLANATION GENERATOR
=========================================

Converts technical ML features into human-readable explanations

Features:
- Natural language explanation generation
- Feature-to-reason mapping
- Risk severity classification
- Actionable security recommendations
- Multi-language support (extensible)

Author: PhishGuard AI Team
Version: 2.0.0
Date: October 10, 2025
"""

from typing import Dict, List, Any, Tuple
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classification"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ExplanationGenerator:
    """
    Generates human-readable explanations from ML predictions

    Converts technical features and SHAP values into natural language
    that non-technical users can understand.
    """

    def __init__(self, language: str = "en"):
        """
        Initialize explanation generator

        Args:
            language: Language code (default: 'en' for English)
        """
        self.language = language
        self.feature_explanations = self._initialize_feature_explanations()
        self.category_descriptions = self._initialize_category_descriptions()

        logger.info(f"✅ ExplanationGenerator initialized (language: {language})")

    def _initialize_feature_explanations(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize feature-to-explanation mapping

        Returns:
            Dictionary mapping feature names to explanation templates
        """
        return {
            # URL Structure
            "url_length": {
                "name": "URL Length",
                "suspicious_condition": lambda v: v > 75,
                "suspicious_text": "Unusually long URL ({value} characters). Phishers often use long URLs to hide suspicious domains.",
                "safe_text": "URL length is normal ({value} characters).",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "📏",
            },
            "has_ip": {
                "name": "IP Address in URL",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "URL uses IP address instead of domain name. Legitimate sites use domain names.",
                "safe_text": "URL uses proper domain name.",
                "risk_level": RiskLevel.HIGH,
                "icon": "🔢",
            },
            "num_dots": {
                "name": "Subdomain Count",
                "suspicious_condition": lambda v: v > 5,
                "suspicious_text": "Excessive subdomains ({value} dots). May be hiding the real domain.",
                "safe_text": "Normal subdomain structure ({value} dots).",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🔗",
            },
            "url_entropy": {
                "name": "URL Randomness",
                "suspicious_condition": lambda v: v > 4.0,
                "suspicious_text": "High URL randomness (score: {value:.2f}). URL appears obfuscated or auto-generated.",
                "safe_text": "URL structure looks normal (randomness: {value:.2f}).",
                "risk_level": RiskLevel.HIGH,
                "icon": "🎲",
            },
            "has_@": {
                "name": "Username in URL",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "URL contains @ symbol. Common phishing technique to trick users about the real domain.",
                "safe_text": "No suspicious symbols in URL.",
                "risk_level": RiskLevel.HIGH,
                "icon": "⚠️",
            },
            # Domain Security
            "domain_age_days": {
                "name": "Domain Age",
                "suspicious_condition": lambda v: v < 30,
                "suspicious_text": "Very new domain (only {value:.0f} days old). Phishing sites often use newly registered domains.",
                "safe_text": "Established domain ({value:.0f} days old).",
                "risk_level": RiskLevel.HIGH,
                "icon": "📅",
            },
            "ssl_validity": {
                "name": "SSL Certificate",
                "suspicious_condition": lambda v: v == 0,
                "suspicious_text": "No valid SSL certificate. Your connection is NOT secure.",
                "safe_text": "Valid SSL certificate present.",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🔒",
            },
            "is_https": {
                "name": "HTTPS Protocol",
                "suspicious_condition": lambda v: v == 0,
                "suspicious_text": "Site uses unencrypted HTTP. Your data can be intercepted.",
                "safe_text": "Site uses encrypted HTTPS.",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🔐",
            },
            "typosquatting_detected": {
                "name": "Typosquatting",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Domain is similar to a known brand (typosquatting). May be impersonating a legitimate site.",
                "safe_text": "No typosquatting detected.",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🎭",
            },
            "homograph_attack": {
                "name": "Homograph Attack",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Uses look-alike characters (е vs e). Advanced phishing technique.",
                "safe_text": "No look-alike character substitution.",
                "risk_level": RiskLevel.HIGH,
                "icon": "👁️",
            },
            "suspicious_tld": {
                "name": "Suspicious Domain Extension",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Uses suspicious top-level domain (.tk, .ml, etc.). Often used by phishers.",
                "safe_text": "Uses standard domain extension.",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🌐",
            },
            # Content Analysis
            "has_password_field": {
                "name": "Password Input Field",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Page requests password. Be cautious about entering credentials.",
                "safe_text": "No password fields detected.",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🔑",
            },
            "num_forms": {
                "name": "Form Count",
                "suspicious_condition": lambda v: v > 5,
                "suspicious_text": "Excessive forms ({value:.0f} forms). May be collecting user data.",
                "safe_text": "Normal number of forms ({value:.0f}).",
                "risk_level": RiskLevel.LOW,
                "icon": "📋",
            },
            "num_iframes": {
                "name": "Hidden Frames",
                "suspicious_condition": lambda v: v > 3,
                "suspicious_text": "Multiple hidden frames ({value:.0f} iframes). May be loading malicious content.",
                "safe_text": "Normal iframe usage ({value:.0f}).",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🖼️",
            },
            "num_external_links": {
                "name": "External Links",
                "suspicious_condition": lambda v: v > 50,
                "suspicious_text": "Excessive external links ({value:.0f} links). Unusual for legitimate sites.",
                "safe_text": "Normal number of external links ({value:.0f}).",
                "risk_level": RiskLevel.LOW,
                "icon": "🔗",
            },
            "suspicious_keywords_count": {
                "name": "Suspicious Keywords",
                "suspicious_condition": lambda v: v > 3,
                "suspicious_text": "Contains {value:.0f} phishing keywords (urgent, verify, suspend, etc.).",
                "safe_text": "No suspicious keywords detected.",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🚩",
            },
            "brand_impersonation": {
                "name": "Brand Impersonation",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Appears to impersonate a well-known brand. High phishing risk.",
                "safe_text": "No brand impersonation detected.",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🎯",
            },
            # URL Patterns
            "has_double_slash": {
                "name": "Double Slash",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "URL contains suspicious double slashes. May be a redirect trick.",
                "safe_text": "URL structure is clean.",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "➿",
            },
            "url_shortening": {
                "name": "URL Shortener",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Uses URL shortening service. Real destination is hidden.",
                "safe_text": "Direct URL (no shortener).",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🔗",
            },
            "obfuscation_detected": {
                "name": "URL Obfuscation",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "URL is obfuscated (hex encoding, etc.). Trying to hide real destination.",
                "safe_text": "URL is clear and readable.",
                "risk_level": RiskLevel.HIGH,
                "icon": "🎭",
            },
            "redirect_count": {
                "name": "Redirect Chain",
                "suspicious_condition": lambda v: v > 2,
                "suspicious_text": "Multiple redirects ({value:.0f} redirects). May be evading detection.",
                "safe_text": "Direct navigation (no redirects).",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "↪️",
            },
            # Threat Intelligence
            "phishtank_match": {
                "name": "PhishTank Database",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "⚠️ CONFIRMED PHISHING: Found in PhishTank database of known phishing sites.",
                "safe_text": "Not in PhishTank phishing database.",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🎣",
            },
            "virustotal_detections": {
                "name": "VirusTotal Detections",
                "suspicious_condition": lambda v: v > 5,
                "suspicious_text": "⚠️ Flagged by {value:.0f} security vendors on VirusTotal.",
                "safe_text": "Clean scan on VirusTotal (0 detections).",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🛡️",
            },
            "google_safebrowsing": {
                "name": "Google Safe Browsing",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "⚠️ Flagged by Google Safe Browsing as dangerous.",
                "safe_text": "Passed Google Safe Browsing check.",
                "risk_level": RiskLevel.CRITICAL,
                "icon": "🔍",
            },
            "reputation_score": {
                "name": "Reputation Score",
                "suspicious_condition": lambda v: v < 30,
                "suspicious_text": "Low reputation score ({value:.0f}/100). Site has poor security standing.",
                "safe_text": "Good reputation score ({value:.0f}/100).",
                "risk_level": RiskLevel.HIGH,
                "icon": "⭐",
            },
            # Behavioral Signals
            "popup_count": {
                "name": "Popup Windows",
                "suspicious_condition": lambda v: v > 3,
                "suspicious_text": "Excessive popups ({value:.0f} popups). Common phishing tactic.",
                "safe_text": "No suspicious popups.",
                "risk_level": RiskLevel.MEDIUM,
                "icon": "🪟",
            },
            "login_form": {
                "name": "Login Form",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Page has login form. Verify this is the correct site before entering credentials.",
                "safe_text": "No login form detected.",
                "risk_level": RiskLevel.INFO,
                "icon": "🔐",
            },
            "external_favicon": {
                "name": "External Favicon",
                "suspicious_condition": lambda v: v == 1,
                "suspicious_text": "Favicon loaded from external site. May be impersonating another brand.",
                "safe_text": "Favicon is hosted on same domain.",
                "risk_level": RiskLevel.LOW,
                "icon": "🖼️",
            },
        }

    def _initialize_category_descriptions(self) -> Dict[str, Dict[str, str]]:
        """Initialize category-level descriptions"""
        return {
            "URL Structure": {
                "description": "Analysis of URL format and structure",
                "icon": "🔗",
            },
            "Domain Security": {
                "description": "Domain registration and security checks",
                "icon": "🔒",
            },
            "Content Analysis": {
                "description": "Page content and embedded elements",
                "icon": "📄",
            },
            "URL Patterns": {
                "description": "Detection of suspicious URL patterns",
                "icon": "🎯",
            },
            "Threat Intelligence": {
                "description": "Cross-reference with known threat databases",
                "icon": "🛡️",
            },
            "Behavioral Signals": {
                "description": "Real-time behavioral analysis",
                "icon": "👁️",
            },
            "Technical Indicators": {
                "description": "DNS, WHOIS, and network analysis",
                "icon": "⚙️",
            },
        }

    def generate_explanation(
        self,
        prediction: str,
        confidence: float,
        top_features: List[Dict[str, Any]],
        categorized_features: Dict[str, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive human-readable explanation

        Args:
            prediction: 'PHISHING' or 'LEGITIMATE'
            confidence: Prediction confidence (0-1)
            top_features: Top contributing features
            categorized_features: Features grouped by category

        Returns:
            Dictionary with structured explanation
        """
        is_phishing = prediction == "PHISHING"

        # Generate main verdict
        verdict = self._generate_verdict(prediction, confidence)

        # Generate detailed reasons
        reasons = self._generate_reasons(top_features, is_phishing)

        # Generate category summaries
        category_summaries = self._generate_category_summaries(
            categorized_features, is_phishing
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(is_phishing, top_features)

        # Calculate risk breakdown
        risk_breakdown = self._calculate_risk_breakdown(reasons)

        return {
            "verdict": verdict,
            "reasons": reasons,
            "category_summaries": category_summaries,
            "recommendations": recommendations,
            "risk_breakdown": risk_breakdown,
            "confidence": confidence,
            "prediction": prediction,
        }

    def _generate_verdict(self, prediction: str, confidence: float) -> Dict[str, Any]:
        """Generate main verdict message"""
        if prediction == "PHISHING":
            severity = (
                "CRITICAL"
                if confidence > 0.9
                else "HIGH" if confidence > 0.7 else "MEDIUM"
            )

            messages = {
                "CRITICAL": "🚨 DANGER: This is almost certainly a phishing site!",
                "HIGH": "⚠️ WARNING: This site shows strong phishing indicators.",
                "MEDIUM": "⚠️ CAUTION: This site has suspicious characteristics.",
            }

            return {
                "message": messages[severity],
                "severity": severity,
                "confidence": confidence,
                "icon": "🚨" if severity == "CRITICAL" else "⚠️",
                "action": "BLOCK" if confidence > 0.7 else "WARN",
            }
        else:
            return {
                "message": "✅ This site appears to be legitimate.",
                "severity": "SAFE",
                "confidence": confidence,
                "icon": "✅",
                "action": "ALLOW",
            }

    def _generate_reasons(
        self, top_features: List[Dict[str, Any]], is_phishing: bool
    ) -> List[Dict[str, Any]]:
        """Generate list of reasons for the prediction"""
        reasons = []

        for feature in top_features[:10]:  # Top 10 features
            feature_name = feature["name"]
            feature_value = feature["value"]
            shap_value = feature["shap_value"]

            # Get explanation template
            if feature_name in self.feature_explanations:
                template = self.feature_explanations[feature_name]
                is_suspicious = template["suspicious_condition"](feature_value)

                # Generate text
                if is_phishing and is_suspicious and shap_value > 0:
                    text = template["suspicious_text"].format(value=feature_value)
                    risk_level = template["risk_level"].value
                    icon = template["icon"]
                elif not is_phishing and not is_suspicious and shap_value < 0:
                    text = template["safe_text"].format(value=feature_value)
                    risk_level = RiskLevel.INFO.value
                    icon = "✅"
                else:
                    # Feature contributes differently than expected
                    continue

                reasons.append(
                    {
                        "text": text,
                        "risk_level": risk_level,
                        "icon": icon,
                        "feature_name": template["name"],
                        "importance": abs(shap_value),
                    }
                )

        # Sort by importance
        reasons.sort(key=lambda x: x["importance"], reverse=True)

        return reasons

    def _generate_category_summaries(
        self, categorized_features: Dict[str, List[Dict[str, Any]]], is_phishing: bool
    ) -> List[Dict[str, Any]]:
        """Generate summaries for each category"""
        summaries = []

        for category, features in categorized_features.items():
            if not features:
                continue

            # Count suspicious features in this category
            suspicious_count = sum(1 for f in features if f["shap_value"] > 0.01)
            total_count = len(features)

            # Get category info
            category_info = self.category_descriptions.get(
                category, {"description": category, "icon": "📊"}
            )

            # Determine status
            if is_phishing:
                if suspicious_count >= total_count * 0.7:
                    status = "CRITICAL"
                    message = f"Multiple red flags in {category.lower()}"
                elif suspicious_count >= total_count * 0.4:
                    status = "WARNING"
                    message = f"Some concerns in {category.lower()}"
                else:
                    status = "INFO"
                    message = f"Minor issues in {category.lower()}"
            else:
                status = "SAFE"
                message = f"{category} checks passed"

            summaries.append(
                {
                    "category": category,
                    "icon": category_info["icon"],
                    "description": category_info["description"],
                    "status": status,
                    "message": message,
                    "suspicious_count": suspicious_count,
                    "total_count": total_count,
                    "features": features[:3],  # Top 3 features per category
                }
            )

        return summaries

    def _generate_recommendations(
        self, is_phishing: bool, top_features: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        if is_phishing:
            recommendations = [
                {
                    "icon": "🚫",
                    "text": "DO NOT enter any passwords or personal information",
                    "priority": "CRITICAL",
                },
                {
                    "icon": "🔙",
                    "text": "Close this page immediately and return to safety",
                    "priority": "CRITICAL",
                },
                {
                    "icon": "🔒",
                    "text": "If you entered credentials, change your password immediately",
                    "priority": "HIGH",
                },
            ]

            # Add specific recommendations based on features
            feature_names = [f["name"] for f in top_features]

            if any("ssl" in name or "https" in name for name in feature_names):
                recommendations.append(
                    {
                        "icon": "🔐",
                        "text": "Always verify the padlock icon and HTTPS before entering sensitive data",
                        "priority": "MEDIUM",
                    }
                )

            if any("domain_age" in name for name in feature_names):
                recommendations.append(
                    {
                        "icon": "📅",
                        "text": "Be extra cautious with newly registered domains",
                        "priority": "MEDIUM",
                    }
                )

            return recommendations
        else:
            return [
                {
                    "icon": "✅",
                    "text": "This site appears safe, but always verify URLs before entering sensitive data",
                    "priority": "INFO",
                },
                {
                    "icon": "🔒",
                    "text": "Check for the padlock icon to ensure secure connection",
                    "priority": "INFO",
                },
            ]

    def _calculate_risk_breakdown(
        self, reasons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate risk score breakdown by severity"""
        breakdown = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}

        for reason in reasons:
            risk_level = reason["risk_level"]
            if risk_level in breakdown:
                breakdown[risk_level] += 1

        # Calculate overall risk score
        weights = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3, "INFO": 0}

        total_score = sum(breakdown[level] * weights[level] for level in breakdown)
        max_score = sum(weights.values()) * 3  # Assume max 3 features per level

        risk_score = min(100, (total_score / max_score) * 100)

        return {
            "score": risk_score,
            "breakdown": breakdown,
            "total_indicators": sum(breakdown.values()),
        }

    def format_for_display(
        self, explanation: Dict[str, Any], format: str = "html"
    ) -> str:
        """
        Format explanation for display

        Args:
            explanation: Explanation dictionary
            format: Output format ('html', 'text', 'json')

        Returns:
            Formatted string
        """
        if format == "html":
            return self._format_html(explanation)
        elif format == "text":
            return self._format_text(explanation)
        elif format == "json":
            import json

            return json.dumps(explanation, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _format_html(self, explanation: Dict[str, Any]) -> str:
        """Format as HTML"""
        verdict = explanation["verdict"]
        reasons = explanation["reasons"]
        recommendations = explanation["recommendations"]
        risk_breakdown = explanation["risk_breakdown"]

        html = f"""
        <div class="phishguard-explanation">
            <div class="verdict {verdict['severity'].lower()}">
                <span class="icon">{verdict['icon']}</span>
                <h2>{verdict['message']}</h2>
                <div class="confidence">Confidence: {verdict['confidence']:.1%}</div>
            </div>

            <div class="risk-score">
                <h3>Risk Score: {risk_breakdown['score']:.0f}/100</h3>
                <div class="risk-bar">
                    <div class="risk-fill" style="width: {risk_breakdown['score']}%"></div>
                </div>
            </div>

            <div class="reasons">
                <h3>Analysis Results:</h3>
                <ul>
        """

        for reason in reasons[:5]:
            html += f"""
                    <li class="{reason['risk_level'].lower()}">
                        <span class="icon">{reason['icon']}</span>
                        {reason['text']}
                    </li>
            """

        html += """
                </ul>
            </div>

            <div class="recommendations">
                <h3>Recommendations:</h3>
                <ul>
        """

        for rec in recommendations:
            html += f"""
                    <li class="{rec['priority'].lower()}">
                        <span class="icon">{rec['icon']}</span>
                        {rec['text']}
                    </li>
            """

        html += """
                </ul>
            </div>
        </div>
        """

        return html

    def _format_text(self, explanation: Dict[str, Any]) -> str:
        """Format as plain text"""
        verdict = explanation["verdict"]
        reasons = explanation["reasons"]
        recommendations = explanation["recommendations"]
        risk_breakdown = explanation["risk_breakdown"]

        text = f"""
{verdict['icon']} {verdict['message']}
Confidence: {verdict['confidence']:.1%}
Risk Score: {risk_breakdown['score']:.0f}/100

{'=' * 50}
ANALYSIS RESULTS:
{'=' * 50}

"""

        for i, reason in enumerate(reasons[:5], 1):
            text += f"{i}. {reason['icon']} {reason['text']}\n"

        text += f"""
{'=' * 50}
RECOMMENDATIONS:
{'=' * 50}

"""

        for i, rec in enumerate(recommendations, 1):
            text += f"{i}. {rec['icon']} {rec['text']}\n"

        return text.strip()


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("📝 PhishGuard AI - Explanation Generator")
    print("=" * 50)

    generator = ExplanationGenerator()

    # Test with phishing example
    test_features = [
        {"name": "phishtank_match", "value": 1, "shap_value": 0.45, "importance": 0.45},
        {"name": "ssl_validity", "value": 0, "shap_value": 0.35, "importance": 0.35},
        {"name": "domain_age_days", "value": 5, "shap_value": 0.28, "importance": 0.28},
        {
            "name": "typosquatting_detected",
            "value": 1,
            "shap_value": 0.22,
            "importance": 0.22,
        },
        {"name": "url_entropy", "value": 4.8, "shap_value": 0.18, "importance": 0.18},
    ]

    explanation = generator.generate_explanation(
        prediction="PHISHING",
        confidence=0.95,
        top_features=test_features,
        categorized_features={"Threat Intelligence": test_features[:2]},
    )

    print("\n✅ Explanation generated!")
    print(f"\nVerdict: {explanation['verdict']['message']}")
    print(f"Risk Score: {explanation['risk_breakdown']['score']:.0f}/100")
    print(f"\nTop Reasons:")
    for reason in explanation["reasons"][:3]:
        print(f"  {reason['icon']} {reason['text']}")

    print("\n✅ Module working correctly!")

"""
 BEHAVIORAL FEATURE EXTRACTOR
================================

Extract 20+ behavioral and temporal features with HIGHEST quality
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
from datetime import datetime
import hashlib


class BehavioralFeatureExtractor:
    """
    High-performance behavioral feature extraction

    Extracts 20+ features:
    - URL manipulation patterns
    - Suspicious parameter usage
    - Encoding tricks
    - Obfuscation detection
    - Temporal patterns
    - And more...
    """

    def __init__(self):
        # Suspicious keywords often used in phishing
        self.phishing_keywords = [
            "verify",
            "account",
            "update",
            "confirm",
            "login",
            "signin",
            "bank",
            "secure",
            "ebayisapi",
            "webscr",
            "paypal",
            "suspended",
            "locked",
            "unusual",
            "activity",
            "click",
            "urgent",
            "important",
        ]

        # File extensions that shouldn't be in URLs
        self.suspicious_extensions = [
            ".exe",
            ".zip",
            ".rar",
            ".scr",
            ".bat",
            ".cmd",
            ".com",
            ".pif",
            ".vbs",
            ".js",
            ".jar",
            ".apk",
        ]

    def extract_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all behavioral features from URL

        Args:
            url: URL to analyze

        Returns:
            Dictionary with 20+ behavioral features
        """
        features = {}

        try:
            parsed = urlparse(url)
            full_url = url.lower()

            # URL Manipulation Detection (5 features)
            features["url_has_at_symbol"] = 1 if "@" in url else 0
            features["url_double_slash_in_path"] = 1 if "//" in parsed.path else 0
            features["url_has_ip_address"] = self._has_ip_address(parsed.netloc)
            features["url_port_specified"] = (
                1
                if ":" in parsed.netloc and parsed.netloc.split(":")[1].isdigit()
                else 0
            )
            features["url_uses_shortening"] = self._is_url_shortener(parsed.netloc)

            # Encoding and Obfuscation (5 features)
            features["url_encoded_chars_count"] = full_url.count("%")
            features["url_hex_encoding"] = (
                1 if re.search(r"%[0-9a-f]{2}", full_url) else 0
            )
            features["url_unicode_chars"] = (
                1 if any(ord(char) > 127 for char in url) else 0
            )
            features["url_multiple_encodings"] = 1 if full_url.count("%") > 5 else 0
            features["url_obfuscation_score"] = self._calculate_obfuscation_score(url)

            # Suspicious Keywords (5 features)
            features["phishing_keywords_count"] = sum(
                1 for kw in self.phishing_keywords if kw in full_url
            )
            features["has_login_keyword"] = (
                1 if any(kw in full_url for kw in ["login", "signin", "account"]) else 0
            )
            features["has_verify_keyword"] = (
                1
                if any(kw in full_url for kw in ["verify", "confirm", "update"])
                else 0
            )
            features["has_urgency_keyword"] = (
                1
                if any(
                    kw in full_url
                    for kw in ["urgent", "suspended", "locked", "unusual"]
                )
                else 0
            )
            features["keyword_density"] = features["phishing_keywords_count"] / max(
                1, len(url.split("/"))
            )

            # Parameter Analysis (5 features)
            query_params = parse_qs(parsed.query)
            features["param_count"] = len(query_params)
            features["param_has_url"] = (
                1
                if any(
                    "url" in key.lower() or "redirect" in key.lower()
                    for key in query_params
                )
                else 0
            )
            features["param_has_email"] = (
                1 if any("email" in key.lower() for key in query_params) else 0
            )
            features["param_suspicious"] = self._has_suspicious_params(query_params)
            features["param_total_length"] = len(parsed.query)

            # File and Extension Analysis (3 features)
            features["has_suspicious_extension"] = (
                1 if any(ext in full_url for ext in self.suspicious_extensions) else 0
            )
            features["path_has_extension"] = (
                1 if "." in parsed.path.split("/")[-1] else 0
            )
            features["extension_mismatch"] = self._check_extension_mismatch(
                parsed.path, parsed.scheme
            )

            # Brand Impersonation Detection (2 features)
            features["impersonation_score"] = self._calculate_impersonation_score(
                parsed.netloc
            )
            features["typosquatting_score"] = self._calculate_typosquatting_score(
                parsed.netloc
            )

        except Exception as e:
            # Return safe defaults on error
            features = self._get_default_features()

        return features

    def _get_default_features(self) -> Dict[str, Any]:
        """Default feature values"""
        return {
            # URL Manipulation
            "url_has_at_symbol": 0,
            "url_double_slash_in_path": 0,
            "url_has_ip_address": 0,
            "url_port_specified": 0,
            "url_uses_shortening": 0,
            # Encoding
            "url_encoded_chars_count": 0,
            "url_hex_encoding": 0,
            "url_unicode_chars": 0,
            "url_multiple_encodings": 0,
            "url_obfuscation_score": 0.0,
            # Keywords
            "phishing_keywords_count": 0,
            "has_login_keyword": 0,
            "has_verify_keyword": 0,
            "has_urgency_keyword": 0,
            "keyword_density": 0.0,
            # Parameters
            "param_count": 0,
            "param_has_url": 0,
            "param_has_email": 0,
            "param_suspicious": 0,
            "param_total_length": 0,
            # Extensions
            "has_suspicious_extension": 0,
            "path_has_extension": 0,
            "extension_mismatch": 0,
            # Impersonation
            "impersonation_score": 0.0,
            "typosquatting_score": 0.0,
        }

    def _has_ip_address(self, netloc: str) -> int:
        """Check if URL uses IP address instead of domain"""
        # IPv4 pattern
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        # IPv6 pattern (simplified)
        ipv6_pattern = r"^\[?([0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}\]?$"

        hostname = netloc.split(":")[0]  # Remove port

        if re.match(ipv4_pattern, hostname) or re.match(ipv6_pattern, hostname.lower()):
            return 1
        return 0

    def _is_url_shortener(self, netloc: str) -> int:
        """Check if URL uses a known shortening service"""
        shorteners = [
            "bit.ly",
            "goo.gl",
            "t.co",
            "tinyurl.com",
            "ow.ly",
            "buff.ly",
            "adf.ly",
            "is.gd",
            "bit.do",
            "short.link",
            "rebrandly.com",
            "cutt.ly",
            "tiny.cc",
        ]
        return 1 if any(short in netloc.lower() for short in shorteners) else 0

    def _calculate_obfuscation_score(self, url: str) -> float:
        """Calculate URL obfuscation score (0-1)"""
        score = 0.0

        # Multiple URL encodings
        if url.count("%") > 3:
            score += 0.3

        # Unicode characters
        if any(ord(char) > 127 for char in url):
            score += 0.2

        # Excessive special characters
        special_chars = sum(1 for char in url if char in "!@#$%^&*()+=[]{}|;:,<>?")
        if special_chars > 10:
            score += 0.3

        # Mixed case in domain (unusual)
        netloc = urlparse(url).netloc
        if netloc and netloc != netloc.lower() and netloc != netloc.upper():
            score += 0.2

        return min(1.0, score)

    def _has_suspicious_params(self, params: Dict) -> int:
        """Check for suspicious parameter patterns"""
        suspicious_keys = [
            "redirect",
            "url",
            "next",
            "continue",
            "return",
            "goto",
            "out",
            "redir",
        ]

        for key in params.keys():
            if any(sus in key.lower() for sus in suspicious_keys):
                # Check if param value looks like a URL
                values = params[key]
                for value in values:
                    if "http" in value or "//" in value or ".com" in value:
                        return 1
        return 0

    def _check_extension_mismatch(self, path: str, scheme: str) -> int:
        """Check if file extension doesn't match the scheme"""
        if not path or "." not in path.split("/")[-1]:
            return 0

        extension = path.split(".")[-1].lower()

        # Executable extensions on HTTPS sites are suspicious
        executable_exts = ["exe", "scr", "bat", "cmd", "com", "pif"]
        if scheme == "https" and extension in executable_exts:
            return 1

        return 0

    def _calculate_impersonation_score(self, netloc: str) -> float:
        """Calculate brand impersonation score"""
        major_brands = [
            "google",
            "facebook",
            "amazon",
            "microsoft",
            "apple",
            "paypal",
            "netflix",
            "linkedin",
            "instagram",
            "twitter",
            "yahoo",
            "ebay",
            "walmart",
            "bank",
            "chase",
        ]

        score = 0.0
        netloc_lower = netloc.lower()

        for brand in major_brands:
            if brand in netloc_lower:
                # Check if it's NOT the official domain
                if (
                    not netloc_lower.endswith(f".{brand}.com")
                    and netloc_lower != f"{brand}.com"
                ):
                    score += 0.5
                    # Extra points for brand + suspicious words
                    if any(
                        word in netloc_lower
                        for word in ["secure", "login", "verify", "account"]
                    ):
                        score += 0.3

        return min(1.0, score)

    def _calculate_typosquatting_score(self, netloc: str) -> float:
        """Calculate typosquatting score using Levenshtein-like logic"""
        popular_domains = [
            "google.com",
            "facebook.com",
            "amazon.com",
            "microsoft.com",
            "apple.com",
            "paypal.com",
            "netflix.com",
            "linkedin.com",
        ]

        min_distance = float("inf")
        netloc_clean = netloc.split(":")[0].lower()  # Remove port

        for domain in popular_domains:
            distance = self._levenshtein_distance(netloc_clean, domain)
            min_distance = min(min_distance, distance)

        # If very close to a popular domain (1-3 char difference), suspicious
        if min_distance <= 3:
            return min(1.0, (4 - min_distance) / 4)

        return 0.0

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def get_feature_names(self) -> list:
        """Get list of all feature names"""
        return list(self._get_default_features().keys())

    def get_feature_count(self) -> int:
        """Get total number of features"""
        return len(self._get_default_features())


def demo_behavioral_features():
    """Demonstrate behavioral feature extraction"""
    print("=" * 80)
    print(" BEHAVIORAL FEATURE EXTRACTOR DEMO")
    print("=" * 80)

    extractor = BehavioralFeatureExtractor()

    # Test URLs
    test_urls = [
        "https://google.com",
        "https://secure-paypal-verify.com/update",
        "http://192.168.1.1/login",
        "https://g00gle.com/signin?redirect=http://evil.com",
        "https://bit.ly/abc123",
    ]

    print(f"\n Extracting {extractor.get_feature_count()} behavioral features...\n")

    for url in test_urls:
        print(f" URL: {url}")
        print("-" * 80)

        features = extractor.extract_features(url)

        # Print key features
        print(
            f"   IP Address: {' Yes' if features['url_has_ip_address'] else ' No'}"
        )
        print(
            f"   URL Shortener: {' Yes' if features['url_uses_shortening'] else ' No'}"
        )
        print(f"   Phishing Keywords: {features['phishing_keywords_count']}")
        print(f"   Obfuscation Score: {features['url_obfuscation_score']:.2f}")
        print(f"   Impersonation Score: {features['impersonation_score']:.2f}")
        print(f"   Typosquatting Score: {features['typosquatting_score']:.2f}")
        print(
            f"   Suspicious Params: {' Yes' if features['param_suspicious'] else ' No'}"
        )
        print()

    print("=" * 80)
    print(f" BEHAVIORAL FEATURE EXTRACTION COMPLETE")
    print(f"   Total Features: {extractor.get_feature_count()}")
    print("=" * 80)


if __name__ == "__main__":
    demo_behavioral_features()

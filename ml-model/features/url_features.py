"""
URL Feature Extraction Module - 30+ Advanced Features
Analyzes URL structure, patterns, and characteristics
"""

import re
import math
from urllib.parse import urlparse, parse_qs
from collections import Counter
import tldextract
from Levenshtein import distance as levenshtein_distance
import idna
from typing import Dict, Any
import numpy as np


class URLFeatureExtractor:
    """Extract 30+ features from URL for phishing detection"""

    def __init__(self):
        # Top 100 legitimate domains for typosquatting detection
        self.legitimate_domains = [
            "google",
            "facebook",
            "youtube",
            "amazon",
            "wikipedia",
            "yahoo",
            "reddit",
            "twitter",
            "instagram",
            "linkedin",
            "netflix",
            "microsoft",
            "apple",
            "paypal",
            "ebay",
            "pinterest",
            "craigslist",
            "imdb",
            "stackoverflow",
            "github",
        ]

        self.suspicious_keywords = [
            "login",
            "signin",
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
            "validation",
            "authentication",
            "password",
            "credential",
        ]

        self.suspicious_tlds = [
            ".tk",
            ".ml",
            ".ga",
            ".cf",
            ".gq",
            ".xyz",
            ".top",
            ".online",
            ".work",
            ".click",
            ".link",
            ".bid",
            ".loan",
            ".download",
            ".win",
        ]

    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all 30 URL features

        Returns:
            Dictionary with 30 URL features
        """
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)

            features = {}

            # ===== BASIC FEATURES (1-10) =====
            features["url_length"] = len(url)
            features["domain_length"] = len(extracted.domain)
            features["path_length"] = len(parsed.path)
            features["query_length"] = len(parsed.query)
            features["fragment_length"] = len(parsed.fragment)

            features["num_dots"] = url.count(".")
            features["num_hyphens"] = url.count("-")
            features["num_underscores"] = url.count("_")
            features["num_slashes"] = url.count("/")
            features["num_digits"] = sum(c.isdigit() for c in url)

            # ===== SUBDOMAIN FEATURES (11-15) =====
            subdomain = extracted.subdomain
            features["subdomain_length"] = len(subdomain)
            features["num_subdomains"] = subdomain.count(".") + 1 if subdomain else 0
            features["has_www"] = 1 if "www" in subdomain else 0
            features["subdomain_entropy"] = self._calculate_entropy(subdomain)
            features["subdomain_digit_ratio"] = (
                sum(c.isdigit() for c in subdomain) / len(subdomain) if subdomain else 0
            )

            # ===== SPECIAL CHARACTERS (16-20) =====
            features["num_at_symbols"] = url.count("@")
            features["num_ampersands"] = url.count("&")
            features["num_equals"] = url.count("=")
            features["num_question_marks"] = url.count("?")
            features["num_percent"] = url.count("%")

            # ===== SECURITY INDICATORS (21-24) =====
            features["has_https"] = 1 if parsed.scheme == "https" else 0
            features["has_ip_address"] = self._has_ip_address(parsed.netloc)
            features["has_port"] = 1 if parsed.port else 0
            features["port_number"] = parsed.port if parsed.port else 0

            # ===== SUSPICIOUS PATTERNS (25-28) =====
            features["suspicious_keyword_count"] = sum(
                1 for keyword in self.suspicious_keywords if keyword in url.lower()
            )
            features["has_suspicious_tld"] = any(
                url.endswith(tld) for tld in self.suspicious_tlds
            )
            features["url_entropy"] = self._calculate_entropy(url)
            features["vowel_consonant_ratio"] = self._vowel_consonant_ratio(
                extracted.domain
            )

            # ===== TYPOSQUATTING & HOMOGRAPH (29-30) =====
            features["min_levenshtein_distance"] = self._min_levenshtein_distance(
                extracted.domain
            )
            features["has_punycode"] = (
                1 if url.startswith("xn--") or "xn--" in url else 0
            )

            # ===== ADDITIONAL ADVANCED FEATURES (31-35) =====
            features["query_params_count"] = len(parse_qs(parsed.query))
            features["max_subdomain_length"] = max(
                (len(sub) for sub in subdomain.split(".") if sub), default=0
            )
            features["domain_token_count"] = len(
                re.findall(r"[a-zA-Z]+", extracted.domain)
            )
            features["has_redirect_keywords"] = any(
                kw in url.lower() for kw in ["redirect", "redir", "goto", "out", "away"]
            )
            features["special_char_ratio"] = sum(
                1 for c in url if not c.isalnum()
            ) / len(url)

            return features

        except Exception as e:
            print(f"Error extracting URL features: {e}")
            return self._get_default_features()

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of string"""
        if not text:
            return 0.0

        # Calculate character frequency
        counter = Counter(text)
        length = len(text)

        # Calculate entropy
        entropy = 0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _has_ip_address(self, netloc: str) -> int:
        """Check if URL contains IP address instead of domain"""
        # IPv4 pattern
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        # IPv6 pattern (simplified)
        ipv6_pattern = r"^\[?([0-9a-fA-F:]+)\]?$"

        # Remove port if present
        host = netloc.split(":")[0]

        if re.match(ipv4_pattern, host) or re.match(ipv6_pattern, host):
            return 1
        return 0

    def _vowel_consonant_ratio(self, text: str) -> float:
        """Calculate ratio of vowels to consonants"""
        if not text:
            return 0.0

        vowels = sum(1 for c in text.lower() if c in "aeiou")
        consonants = sum(1 for c in text.lower() if c.isalpha() and c not in "aeiou")

        if consonants == 0:
            return 0.0

        return vowels / consonants

    def _min_levenshtein_distance(self, domain: str) -> int:
        """
        Calculate minimum Levenshtein distance to legitimate domains
        Lower distance = likely typosquatting
        """
        if not domain:
            return 999

        min_distance = 999
        for legit_domain in self.legitimate_domains:
            dist = levenshtein_distance(domain.lower(), legit_domain.lower())
            min_distance = min(min_distance, dist)

        return min_distance

    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features in case of error"""
        return {f"url_feature_{i}": 0 for i in range(1, 36)}

    def get_feature_names(self) -> list:
        """Return list of all feature names"""
        return [
            "url_length",
            "domain_length",
            "path_length",
            "query_length",
            "fragment_length",
            "num_dots",
            "num_hyphens",
            "num_underscores",
            "num_slashes",
            "num_digits",
            "subdomain_length",
            "num_subdomains",
            "has_www",
            "subdomain_entropy",
            "subdomain_digit_ratio",
            "num_at_symbols",
            "num_ampersands",
            "num_equals",
            "num_question_marks",
            "num_percent",
            "has_https",
            "has_ip_address",
            "has_port",
            "port_number",
            "suspicious_keyword_count",
            "has_suspicious_tld",
            "url_entropy",
            "vowel_consonant_ratio",
            "min_levenshtein_distance",
            "has_punycode",
            "query_params_count",
            "max_subdomain_length",
            "domain_token_count",
            "has_redirect_keywords",
            "special_char_ratio",
        ]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    extractor = URLFeatureExtractor()

    # Test URLs
    test_urls = [
        "https://www.google.com",
        "http://paypa1.com/verify-account.php?user=123",
        "https://secure-login-amazon.tk/update.html",
        "http://192.168.1.1/admin",
        "https://www.facebok.com/login.php",
    ]

    print("=" * 80)
    print("URL FEATURE EXTRACTION TEST")
    print("=" * 80)

    for url in test_urls:
        print(f"\n🔗 URL: {url}")
        features = extractor.extract_all_features(url)

        print(f"\n📊 Key Features:")
        print(f"   Length: {features['url_length']}")
        print(f"   HTTPS: {'Yes' if features['has_https'] else 'No'}")
        print(f"   Suspicious Keywords: {features['suspicious_keyword_count']}")
        print(f"   URL Entropy: {features['url_entropy']:.2f}")
        print(f"   Min Levenshtein Distance: {features['min_levenshtein_distance']}")
        print(f"   Has IP: {'Yes' if features['has_ip_address'] else 'No'}")
        print(f"   Subdomains: {features['num_subdomains']}")
        print("-" * 80)

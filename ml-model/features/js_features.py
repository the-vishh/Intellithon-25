"""
JavaScript Analysis Feature Extraction Module - 25+ Advanced Features
Analyzes JavaScript code for obfuscation, suspicious APIs, and malicious patterns
"""

from bs4 import BeautifulSoup
import requests
import re
import base64
from typing import Dict, Any
from urllib.parse import urlparse, urljoin


class JSFeatureExtractor:
    """Extract 25+ JavaScript features for phishing detection"""

    def __init__(self):
        self.suspicious_apis = [
            "eval",
            "document.cookie",
            "localStorage",
            "sessionStorage",
            "window.open",
            "document.write",
            "innerHTML",
            "outerHTML",
            "document.location",
            "window.location",
            "XMLHttpRequest",
            "fetch",
            "navigator.clipboard",
        ]

        self.obfuscation_patterns = [
            "eval",
            "unescape",
            "fromCharCode",
            "atob",
            "btoa",
            "String.fromCharCode",
            "decodeURIComponent",
            "escape",
            "charCodeAt",
            "parseInt",
        ]

        self.timeout = 15

    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all 25 JavaScript features

        Returns:
            Dictionary with 25 JS features
        """
        try:
            # Fetch HTML content
            html_content = self._fetch_html(url)

            if not html_content:
                return self._get_default_features()

            soup = BeautifulSoup(html_content, "html.parser")
            parsed_url = urlparse(url)
            base_domain = parsed_url.netloc

            features = {}

            # Extract all scripts
            inline_scripts = []
            external_scripts = []

            for script in soup.find_all("script"):
                if script.get("src"):
                    external_scripts.append(script["src"])
                elif script.string:
                    inline_scripts.append(script.string)

            # Combine all script content
            all_script_content = "\n".join(inline_scripts)

            # ===== BASIC SCRIPT FEATURES (1-5) =====
            features["inline_script_count"] = len(inline_scripts)
            features["external_script_count"] = len(external_scripts)
            features["total_script_length"] = len(all_script_content)
            features["has_inline_scripts"] = 1 if len(inline_scripts) > 0 else 0
            features["has_external_scripts"] = 1 if len(external_scripts) > 0 else 0

            # ===== EXTERNAL SCRIPT ANALYSIS (6-9) =====
            external_domain_count = 0
            suspicious_domains = 0

            for src in external_scripts:
                absolute_url = urljoin(url, src)
                script_domain = urlparse(absolute_url).netloc

                if script_domain and script_domain != base_domain:
                    external_domain_count += 1

                    # Check for suspicious domains
                    if any(
                        sus in script_domain.lower()
                        for sus in [".tk", ".ml", ".ga", "tiny", "bit.ly", "goo.gl"]
                    ):
                        suspicious_domains += 1

            features["external_script_domain_count"] = external_domain_count
            features["suspicious_script_domain_count"] = suspicious_domains
            features["external_script_ratio"] = (
                external_domain_count / len(external_scripts)
                if len(external_scripts) > 0
                else 0
            )

            # Average script size
            avg_script_length = (
                sum(len(s) for s in inline_scripts) / len(inline_scripts)
                if len(inline_scripts) > 0
                else 0
            )
            features["avg_inline_script_length"] = int(avg_script_length)

            # ===== OBFUSCATION DETECTION (10-16) =====
            features["eval_count"] = all_script_content.count("eval(")
            features["unescape_count"] = all_script_content.count("unescape(")
            features["fromcharcode_count"] = all_script_content.lower().count(
                "fromcharcode"
            )
            features["atob_count"] = all_script_content.count("atob(")  # Base64 decode
            features["btoa_count"] = all_script_content.count("btoa(")  # Base64 encode

            # Total obfuscation indicators
            obfuscation_count = sum(
                all_script_content.lower().count(pattern.lower())
                for pattern in self.obfuscation_patterns
            )
            features["total_obfuscation_indicators"] = obfuscation_count

            # Character entropy (high entropy = obfuscation)
            features["script_entropy"] = self._calculate_entropy(all_script_content)

            # ===== SUSPICIOUS API USAGE (17-22) =====
            features["document_cookie_count"] = all_script_content.count(
                "document.cookie"
            )
            features["localstorage_count"] = all_script_content.lower().count(
                "localstorage"
            )
            features["window_open_count"] = all_script_content.count("window.open")
            features["document_write_count"] = all_script_content.count(
                "document.write"
            )
            features["innerhtml_count"] = all_script_content.lower().count("innerhtml")
            features["clipboard_count"] = all_script_content.lower().count("clipboard")

            # ===== ADVANCED ANALYSIS (23-25) =====
            # Long strings (obfuscated code indicator)
            long_string_count = len(
                re.findall(r'["\'][^"\']{100,}["\']', all_script_content)
            )
            features["long_string_count"] = long_string_count

            # Hex encoding
            features["hex_encoded_count"] = len(
                re.findall(r"\\x[0-9a-fA-F]{2}", all_script_content)
            )

            # Comment ratio (low = obfuscated)
            comment_count = all_script_content.count("//") + all_script_content.count(
                "/*"
            )
            features["comment_ratio"] = (
                comment_count / len(all_script_content.split("\n"))
                if all_script_content
                else 0
            )

            # ===== BEHAVIORAL INDICATORS (26-28) =====
            # Auto-redirect
            features["has_auto_redirect"] = self._has_auto_redirect(all_script_content)

            # Form manipulation
            features["has_form_manipulation"] = (
                1
                if "form.submit" in all_script_content.lower()
                or "form.action" in all_script_content.lower()
                else 0
            )

            # Event hijacking
            event_hijack_patterns = [
                "addEventListener",
                "onclick",
                "onload",
                "onsubmit",
                "onkeypress",
                "onchange",
            ]
            event_hijack_count = sum(
                all_script_content.lower().count(pattern.lower())
                for pattern in event_hijack_patterns
            )
            features["event_hijack_count"] = event_hijack_count

            return features

        except Exception as e:
            print(f"Error extracting JS features: {e}")
            return self._get_default_features()

    def _fetch_html(self, url: str) -> str:
        """Fetch HTML content from URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(
                url, headers=headers, timeout=self.timeout, allow_redirects=True
            )
            return response.text
        except Exception as e:
            print(f"Error fetching HTML from {url}: {e}")
            return None

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy (higher = more random/obfuscated)"""
        if not text:
            return 0.0

        from collections import Counter
        import math

        counter = Counter(text)
        length = len(text)

        entropy = 0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _has_auto_redirect(self, script_content: str) -> int:
        """Detect automatic redirects"""
        redirect_patterns = [
            "window.location.href",
            "window.location.replace",
            "location.href",
            "location.replace",
            "document.location",
            'meta http-equiv="refresh"',
        ]

        return (
            1
            if any(pattern in script_content.lower() for pattern in redirect_patterns)
            else 0
        )

    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features in case of error"""
        feature_names = [
            "inline_script_count",
            "external_script_count",
            "total_script_length",
            "has_inline_scripts",
            "has_external_scripts",
            "external_script_domain_count",
            "suspicious_script_domain_count",
            "external_script_ratio",
            "avg_inline_script_length",
            "eval_count",
            "unescape_count",
            "fromcharcode_count",
            "atob_count",
            "btoa_count",
            "total_obfuscation_indicators",
            "script_entropy",
            "document_cookie_count",
            "localstorage_count",
            "window_open_count",
            "document_write_count",
            "innerhtml_count",
            "clipboard_count",
            "long_string_count",
            "hex_encoded_count",
            "comment_ratio",
            "has_auto_redirect",
            "has_form_manipulation",
            "event_hijack_count",
        ]
        return {name: 0 for name in feature_names}

    def get_feature_names(self) -> list:
        """Return list of all feature names"""
        return list(self._get_default_features().keys())


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    extractor = JSFeatureExtractor()

    test_urls = ["https://www.google.com", "https://www.github.com"]

    print("=" * 80)
    print("JAVASCRIPT FEATURE EXTRACTION TEST")
    print("=" * 80)

    for url in test_urls:
        print(f"\n URL: {url}")
        features = extractor.extract_all_features(url)

        print(f"\n Key JavaScript Features:")
        print(f"   Inline Scripts: {features['inline_script_count']}")
        print(f"   External Scripts: {features['external_script_count']}")
        print(f"   Total Script Length: {features['total_script_length']} chars")
        print(f"   Eval Calls: {features['eval_count']}")
        print(f"   Obfuscation Indicators: {features['total_obfuscation_indicators']}")
        print(f"   Script Entropy: {features['script_entropy']:.2f}")
        print(f"   Cookie Access: {features['document_cookie_count']}")
        print(f"   Auto Redirect: {'Yes' if features['has_auto_redirect'] else 'No'}")
        print("-" * 80)

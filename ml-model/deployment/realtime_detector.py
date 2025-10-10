"""
REAL-TIME PHISHING DETECTION ENGINE
Ultra-fast inference engine for Chrome Extension with <50ms total latency
Blocks users BEFORE they reach phishing sites
"""

import numpy as np
import re
from urllib.parse import urlparse
import tldextract
from typing import Dict, Tuple
import time


class RealTimePhishingDetector:
    """
    Lightning-fast phishing detector for real-time blocking

    Architecture:
    1. INSTANT URL-BASED CHECKS (<5ms) - Blacklist, patterns
    2. FAST FEATURE EXTRACTION (<20ms) - Critical features only
    3. ULTRA-FAST ML INFERENCE (<10ms) - Optimized model
    4. TOTAL LATENCY: <50ms for instant blocking
    """

    def __init__(self):
        # Known phishing patterns (instant check)
        self.phishing_keywords = [
            "verify",
            "account",
            "suspend",
            "locked",
            "unusual",
            "confirm",
            "update",
            "secure",
            "banking",
            "paypal",
            "amazon",
            "apple-id",
            "signin",
            "login-",
            "-login",
            "credential",
            "validation",
        ]

        # Suspicious TLDs (instant check)
        self.suspicious_tlds = [
            ".tk",
            ".ml",
            ".ga",
            ".cf",
            ".gq",
            ".xyz",
            ".top",
            ".work",
            ".click",
            ".link",
            ".loan",
            ".download",
            ".racing",
            ".bid",
        ]

        # Trusted domains (whitelist - instant pass)
        self.trusted_domains = {
            "google.com",
            "youtube.com",
            "facebook.com",
            "amazon.com",
            "wikipedia.org",
            "yahoo.com",
            "reddit.com",
            "twitter.com",
            "instagram.com",
            "linkedin.com",
            "netflix.com",
            "microsoft.com",
            "apple.com",
            "github.com",
            "stackoverflow.com",
            "paypal.com",
        }

        # Cached results for super-fast repeat checks
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

        self.models_loaded = False

    def predict_instant(self, url: str) -> Tuple[float, str, Dict]:
        """
        INSTANT phishing prediction with real-time blocking

        Returns:
            (score, verdict, details)
            score: 0.0 (safe) to 1.0 (phishing)
            verdict: 'SAFE', 'SUSPICIOUS', 'PHISHING'
            details: Explanation dictionary
        """
        start_time = time.time()

        # Check cache first (<1ms)
        if url in self.cache:
            cached_result = self.cache[url]
            if time.time() - cached_result["timestamp"] < self.cache_ttl:
                return (
                    cached_result["score"],
                    cached_result["verdict"],
                    cached_result["details"],
                )

        details = {"checks": []}

        # ===== STAGE 1: INSTANT CHECKS (<5ms) =====

        # 1. Whitelist check (instant pass)
        parsed = urlparse(url)
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"

        if domain in self.trusted_domains:
            score = 0.0
            verdict = "SAFE"
            details["checks"].append("✅ Trusted domain")
            self._cache_result(url, score, verdict, details)
            return score, verdict, details

        # 2. URL pattern analysis (instant)
        pattern_score = self._check_url_patterns(url, parsed, extracted, details)

        # If extremely suspicious, block immediately
        if pattern_score > 0.8:
            score = pattern_score
            verdict = "PHISHING"
            details["reason"] = "Highly suspicious URL patterns detected"
            self._cache_result(url, score, verdict, details)
            return score, verdict, details

        # ===== STAGE 2: FAST FEATURE EXTRACTION (<20ms) =====
        critical_features = self._extract_critical_features_fast(
            url, parsed, extracted, details
        )

        # ===== STAGE 3: LIGHTWEIGHT ML INFERENCE (<10ms) =====
        ml_score = self._predict_with_rules(critical_features, details)

        # Combine pattern score and ML score
        final_score = (pattern_score * 0.4) + (ml_score * 0.6)

        # Determine verdict
        if final_score < 0.3:
            verdict = "SAFE"
        elif final_score < 0.7:
            verdict = "SUSPICIOUS"
        else:
            verdict = "PHISHING"

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        details["latency_ms"] = round(latency_ms, 2)
        details["final_score"] = round(final_score, 3)

        # Cache result
        self._cache_result(url, final_score, verdict, details)

        return final_score, verdict, details

    def _check_url_patterns(self, url: str, parsed, extracted, details: Dict) -> float:
        """Ultra-fast URL pattern analysis (<5ms)"""
        score = 0.0
        url_lower = url.lower()

        # Check 1: IP address instead of domain (HIGH RISK)
        if re.match(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url):
            score += 0.4
            details["checks"].append("🚨 IP address in URL")

        # Check 2: Suspicious keywords (HIGH RISK)
        keyword_count = sum(1 for kw in self.phishing_keywords if kw in url_lower)
        if keyword_count >= 2:
            score += 0.3
            details["checks"].append(f"🚨 {keyword_count} suspicious keywords")
        elif keyword_count == 1:
            score += 0.15
            details["checks"].append(f"⚠️  1 suspicious keyword")

        # Check 3: Suspicious TLD (MEDIUM RISK)
        if any(url_lower.endswith(tld) for tld in self.suspicious_tlds):
            score += 0.25
            details["checks"].append("⚠️  Suspicious TLD")

        # Check 4: No HTTPS (MEDIUM RISK)
        if parsed.scheme != "https":
            score += 0.2
            details["checks"].append("⚠️  No HTTPS")

        # Check 5: Excessive subdomains (MEDIUM RISK)
        subdomain = extracted.subdomain
        if subdomain:
            subdomain_count = subdomain.count(".") + 1
            if subdomain_count >= 3:
                score += 0.2
                details["checks"].append(f"⚠️  {subdomain_count} subdomains")

        # Check 6: URL length (MEDIUM RISK)
        if len(url) > 100:
            score += 0.15
            details["checks"].append(f"⚠️  Long URL ({len(url)} chars)")

        # Check 7: @ symbol (HIGH RISK)
        if "@" in url:
            score += 0.3
            details["checks"].append("🚨 @ symbol in URL")

        # Check 8: Suspicious port (MEDIUM RISK)
        if parsed.port and parsed.port not in [80, 443, 8080]:
            score += 0.15
            details["checks"].append(f"⚠️  Unusual port: {parsed.port}")

        # Check 9: Typosquatting indicators
        typo_score = self._check_typosquatting(extracted.domain, details)
        score += typo_score

        return min(score, 1.0)

    def _check_typosquatting(self, domain: str, details: Dict) -> float:
        """Check for typosquatting of popular brands"""
        brands = {
            "google": ["gogle", "googel", "gooogle", "goog1e"],
            "facebook": ["faceboook", "facebok", "faceb00k", "facebk"],
            "paypal": ["paypai", "paypa1", "paypall", "paypa"],
            "amazon": ["amazom", "amaz0n", "amazonn", "amzon"],
            "apple": ["app1e", "appie", "appl3", "aple"],
            "microsoft": ["micros0ft", "micosoft", "microsft"],
            "netflix": ["netfliix", "netfl1x", "netfix"],
            "instagram": ["instagramm", "instagran", "instagrm"],
        }

        domain_lower = domain.lower()

        for brand, typos in brands.items():
            if brand in domain_lower or any(typo in domain_lower for typo in typos):
                # Check if it's exactly the brand (safe) or a typo (dangerous)
                if domain_lower == brand:
                    return 0.0  # Legitimate
                else:
                    details["checks"].append(f"🚨 Possible typosquatting: {brand}")
                    return 0.4

        return 0.0

    def _extract_critical_features_fast(
        self, url: str, parsed, extracted, details: Dict
    ) -> Dict:
        """Extract only critical features for speed (<20ms)"""
        features = {}

        # URL-based features (no network calls)
        features["url_length"] = len(url)
        features["domain_length"] = len(extracted.domain)
        features["path_length"] = len(parsed.path)
        features["num_dots"] = url.count(".")
        features["num_hyphens"] = url.count("-")
        features["num_digits"] = sum(c.isdigit() for c in url)
        features["has_https"] = 1 if parsed.scheme == "https" else 0
        features["has_port"] = 1 if parsed.port else 0
        features["subdomain_count"] = (
            extracted.subdomain.count(".") + 1 if extracted.subdomain else 0
        )

        # Entropy calculation (randomness indicator)
        features["url_entropy"] = self._calculate_entropy(url)
        features["domain_entropy"] = self._calculate_entropy(extracted.domain)

        # Special character ratio
        special_chars = sum(
            1 for c in url if not c.isalnum() and c not in [":", "/", "."]
        )
        features["special_char_ratio"] = special_chars / len(url) if url else 0

        return features

    def _calculate_entropy(self, text: str) -> float:
        """Fast entropy calculation"""
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

    def _predict_with_rules(self, features: Dict, details: Dict) -> float:
        """
        Ultra-fast rule-based prediction (<10ms)
        Uses heuristics instead of complex ML for speed
        """
        score = 0.0

        # Rule 1: URL length
        if features["url_length"] > 75:
            score += 0.15

        # Rule 2: High entropy (random strings)
        if features["domain_entropy"] > 4.0:
            score += 0.2
            details["checks"].append("⚠️  High domain entropy (random strings)")

        # Rule 3: Many hyphens (common in phishing)
        if features["num_hyphens"] > 2:
            score += 0.15
            details["checks"].append("⚠️  Multiple hyphens in URL")

        # Rule 4: No HTTPS
        if features["has_https"] == 0:
            score += 0.2

        # Rule 5: Many subdomains
        if features["subdomain_count"] >= 3:
            score += 0.2

        # Rule 6: High special character ratio
        if features["special_char_ratio"] > 0.15:
            score += 0.15

        # Rule 7: Unusual port
        if features["has_port"] == 1:
            score += 0.1

        return min(score, 1.0)

    def _cache_result(self, url: str, score: float, verdict: str, details: Dict):
        """Cache result for future ultra-fast lookups"""
        self.cache[url] = {
            "score": score,
            "verdict": verdict,
            "details": details,
            "timestamp": time.time(),
        }

    def clear_cache(self):
        """Clear cached results"""
        self.cache.clear()


# ============================================================================
# CHROME EXTENSION INTEGRATION
# ============================================================================


class ChromeExtensionInterface:
    """
    Interface for Chrome Extension
    Provides instant blocking with minimal latency
    """

    def __init__(self):
        self.detector = RealTimePhishingDetector()
        self.stats = {
            "total_checks": 0,
            "phishing_blocked": 0,
            "suspicious_warned": 0,
            "safe_allowed": 0,
            "avg_latency_ms": 0.0,
        }

    def check_url_before_navigation(self, url: str) -> Dict:
        """
        Check URL BEFORE user navigates to it
        Returns decision for Chrome Extension

        Returns:
            {
                'action': 'BLOCK' | 'WARN' | 'ALLOW',
                'score': float,
                'verdict': str,
                'message': str,
                'details': dict,
                'latency_ms': float
            }
        """
        self.stats["total_checks"] += 1

        # Instant prediction
        score, verdict, details = self.detector.predict_instant(url)

        # Determine action
        if verdict == "PHISHING":
            action = "BLOCK"
            message = (
                "🚨 PHISHING DETECTED! This website has been blocked for your safety."
            )
            self.stats["phishing_blocked"] += 1
        elif verdict == "SUSPICIOUS":
            action = "WARN"
            message = "⚠️  SUSPICIOUS WEBSITE! Proceed with extreme caution."
            self.stats["suspicious_warned"] += 1
        else:
            action = "ALLOW"
            message = "✅ Website appears safe."
            self.stats["safe_allowed"] += 1

        # Update average latency
        if "latency_ms" in details:
            total_latency = self.stats["avg_latency_ms"] * (
                self.stats["total_checks"] - 1
            )
            self.stats["avg_latency_ms"] = (
                total_latency + details["latency_ms"]
            ) / self.stats["total_checks"]

        return {
            "action": action,
            "score": score,
            "verdict": verdict,
            "message": message,
            "details": details,
            "latency_ms": details.get("latency_ms", 0),
            "checks_performed": details.get("checks", []),
        }

    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        return self.stats.copy()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("REAL-TIME PHISHING DETECTOR - ULTRA-FAST MODE")
    print("=" * 80)

    # Initialize
    interface = ChromeExtensionInterface()

    # Test URLs
    test_urls = [
        "https://www.google.com",
        "http://paypa1.com/verify-account.php",
        "https://secure-login-amazon.tk/update",
        "http://192.168.1.1/admin",
        "https://www.github.com",
        "http://verify-apple-id.xyz/login",
        "https://faceb00k.com/login.php",
    ]

    print("\n🔍 Testing Real-Time Detection...")
    print("=" * 80)

    for url in test_urls:
        print(f"\n🔗 URL: {url}")
        result = interface.check_url_before_navigation(url)

        print(f"   ⚡ Latency: {result['latency_ms']:.2f}ms")
        print(f"   📊 Score: {result['score']:.3f}")
        print(f"   🎯 Verdict: {result['verdict']}")
        print(f"   🛡️  Action: {result['action']}")
        print(f"   💬 Message: {result['message']}")

        if result["checks_performed"]:
            print(f"   🔍 Checks:")
            for check in result["checks_performed"]:
                print(f"      {check}")

        print("-" * 80)

    # Statistics
    print("\n📈 STATISTICS")
    print("=" * 80)
    stats = interface.get_statistics()
    print(f"   Total Checks: {stats['total_checks']}")
    print(f"   Phishing Blocked: {stats['phishing_blocked']}")
    print(f"   Suspicious Warned: {stats['suspicious_warned']}")
    print(f"   Safe Allowed: {stats['safe_allowed']}")
    print(f"   Average Latency: {stats['avg_latency_ms']:.2f}ms")

    print("\n✅ REAL-TIME DETECTION READY FOR CHROME EXTENSION!")

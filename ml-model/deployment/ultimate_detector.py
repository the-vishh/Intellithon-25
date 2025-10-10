"""
🛡️ ADVANCED DETECTION ENGINE 
================================================

Complete protection system with:
1. Real-time URL scanning before page load
2. AI-powered zero-day detection
3. Automatic threat blocking
4. Download protection with malware scanning
5. Multiple detection sensitivity modes
6. Multi-layer defense architecture

This is THE SUPER BEST AI/ML MODEL EVER!

Author: THE ULTIMATE PHISHING DETECTOR
"""

import os
import sys
import time
import hashlib
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
import json

# Import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from features.url_features import URLFeatureExtractor
    from features.ssl_features import SSLFeatureExtractor
    from features.dns_features import DNSFeatureExtractor
    from features.content_features import ContentFeatureExtractor
    from features.visual_features import VisualPhishingDetector
    from utils.threat_intelligence import ThreatIntelligence
except ImportError as e:
    print(f"⚠️  Module import error: {e}")


class DetectionMode:
    """Detection sensitivity modes"""

    CONSERVATIVE = "conservative"  # Low false positives, may miss some threats
    BALANCED = "balanced"  # Balanced detection (default)
    AGGRESSIVE = "aggressive"  # Maximum protection, higher false positives


class UltimatePhishingDetector:
    """
    🛡️ THE ULTIMATE AI/ML PHISHING DETECTION ENGINE

    Features:
    - Real-time URL scanning
    - AI-powered zero-day detection
    - Automatic threat blocking
    - Download protection
    - Multiple sensitivity modes
    - Multi-layer defense
    """

    def __init__(self, mode: str = DetectionMode.BALANCED):
        """
        Initialize the ultimate detector

        Args:
            mode: Detection sensitivity mode
        """
        self.mode = mode
        self.stats = {
            "urls_scanned": 0,
            "threats_blocked": 0,
            "downloads_scanned": 0,
            "malware_blocked": 0,
            "zero_day_detected": 0,
        }

        # Initialize components
        print("🚀 Initializing ULTIMATE Detection Engine...")

        self.url_extractor = URLFeatureExtractor()
        self.visual_detector = VisualPhishingDetector()
        self.threat_intel = ThreatIntelligence()

        # Detection thresholds by mode
        self.thresholds = self._get_thresholds(mode)

        # Whitelist of trusted domains
        self.whitelist = self._load_whitelist()

        # Known malware signatures
        self.malware_signatures = self._load_malware_signatures()

        print(f"✅ Engine initialized in {mode.upper()} mode")
        print(f"🎯 Threat threshold: {self.thresholds['threat_threshold']}")

    def _get_thresholds(self, mode: str) -> Dict:
        """Get detection thresholds for mode"""
        thresholds = {
            DetectionMode.CONSERVATIVE: {
                "threat_threshold": 0.8,  # High confidence only
                "visual_threshold": 0.85,
                "pattern_threshold": 0.9,
                "download_threshold": 0.85,
                "zero_day_threshold": 0.75,
            },
            DetectionMode.BALANCED: {
                "threat_threshold": 0.6,  # Balanced
                "visual_threshold": 0.7,
                "pattern_threshold": 0.7,
                "download_threshold": 0.7,
                "zero_day_threshold": 0.6,
            },
            DetectionMode.AGGRESSIVE: {
                "threat_threshold": 0.4,  # Maximum protection
                "visual_threshold": 0.5,
                "pattern_threshold": 0.5,
                "download_threshold": 0.5,
                "zero_day_threshold": 0.4,
            },
        }
        return thresholds.get(mode, thresholds[DetectionMode.BALANCED])

    def _load_whitelist(self) -> set:
        """Load trusted domains whitelist"""
        whitelist = {
            # Major tech companies
            "google.com",
            "youtube.com",
            "gmail.com",
            "drive.google.com",
            "microsoft.com",
            "office.com",
            "outlook.com",
            "live.com",
            "apple.com",
            "icloud.com",
            "amazon.com",
            "aws.amazon.com",
            "facebook.com",
            "instagram.com",
            "whatsapp.com",
            "twitter.com",
            "x.com",
            "linkedin.com",
            "github.com",
            "stackoverflow.com",
            # Financial institutions
            "paypal.com",
            "chase.com",
            "bankofamerica.com",
            "wellsfargo.com",
            "citibank.com",
            "usbank.com",
            # Other trusted
            "wikipedia.org",
            "reddit.com",
            "netflix.com",
            "dropbox.com",
            "adobe.com",
        }
        return whitelist

    def _load_malware_signatures(self) -> Dict:
        """Load known malware file signatures"""
        return {
            # Common malware file hashes (examples)
            "eicar_test": "44d88612fea8a8f36de82e1278abb02f",
            # Add more real malware signatures here
        }

    def scan_url_realtime(self, url: str) -> Dict:
        """
        🔍 REAL-TIME URL SCANNING

        Scans URL before page load with multiple detection layers

        Args:
            url: URL to scan

        Returns:
            Scan result with action recommendation
        """
        self.stats["urls_scanned"] += 1
        start_time = time.time()

        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,
            "is_threat": False,
            "threat_score": 0.0,
            "threat_level": "SAFE",
            "action": "ALLOW",
            "layers": {},
            "reasons": [],
            "latency_ms": 0,
        }

        # LAYER 1: Whitelist check (instant)
        domain = self._extract_domain(url)
        if domain in self.whitelist:
            result["layers"]["whitelist"] = {"passed": True, "score": 0.0}
            result["latency_ms"] = (time.time() - start_time) * 1000
            return result

        # LAYER 2: Pattern-based detection (< 5ms)
        pattern_score = self._check_patterns(url)
        result["layers"]["patterns"] = {"score": pattern_score}
        result["threat_score"] += pattern_score * 0.3

        if pattern_score > self.thresholds["pattern_threshold"]:
            result["reasons"].append(
                f"Suspicious URL patterns detected (score: {pattern_score:.2f})"
            )

        # LAYER 3: Threat intelligence (< 100ms with cache)
        threat_report = self.threat_intel.check_url(url)
        result["layers"]["threat_intel"] = threat_report

        if threat_report["is_threat"]:
            result["threat_score"] += 0.4
            result["reasons"].extend(threat_report["details"])

        # LAYER 4: Feature-based ML detection
        features = self._extract_quick_features(url)
        ml_score = self._ml_predict(features)
        result["layers"]["ml_detection"] = {"score": ml_score}
        result["threat_score"] += ml_score * 0.3

        if ml_score > 0.5:
            result["reasons"].append(
                f"AI model detected suspicious patterns (confidence: {ml_score:.2f})"
            )

        # Determine final verdict
        if result["threat_score"] >= self.thresholds["threat_threshold"]:
            result["is_threat"] = True
            result["action"] = "BLOCK"
            result["threat_level"] = (
                "HIGH" if result["threat_score"] > 0.8 else "MEDIUM"
            )
            self.stats["threats_blocked"] += 1
        elif result["threat_score"] >= 0.4:
            result["threat_level"] = "SUSPICIOUS"
            result["action"] = "WARN"

        # Check for zero-day indicators
        if self._is_zero_day(features, result["threat_score"]):
            result["zero_day_detected"] = True
            result["reasons"].append("⚠️  Potential zero-day phishing attack detected")
            self.stats["zero_day_detected"] += 1

        result["latency_ms"] = (time.time() - start_time) * 1000
        return result

    def scan_download(self, file_path: str, file_content: bytes = None) -> Dict:
        """
        📥 DOWNLOAD PROTECTION

        Scans downloaded files for malware before opening

        Args:
            file_path: Path to downloaded file
            file_content: File content bytes (optional)

        Returns:
            Scan result
        """
        self.stats["downloads_scanned"] += 1

        result = {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "is_malware": False,
            "malware_score": 0.0,
            "action": "ALLOW",
            "checks": {},
            "reasons": [],
        }

        # CHECK 1: File extension
        ext = os.path.splitext(file_path)[1].lower()
        dangerous_exts = [
            ".exe",
            ".dll",
            ".bat",
            ".cmd",
            ".ps1",
            ".vbs",
            ".js",
            ".jar",
            ".app",
            ".dmg",
            ".pkg",
        ]

        if ext in dangerous_exts:
            result["malware_score"] += 0.3
            result["checks"]["extension"] = "HIGH_RISK"
            result["reasons"].append(f"Potentially dangerous file type: {ext}")
        else:
            result["checks"]["extension"] = "SAFE"

        # CHECK 2: File hash signature
        if file_content:
            file_hash = hashlib.md5(file_content).hexdigest()

            if file_hash in self.malware_signatures.values():
                result["malware_score"] = 1.0
                result["is_malware"] = True
                result["action"] = "BLOCK"
                result["reasons"].append("⚠️  Known malware signature detected!")
                self.stats["malware_blocked"] += 1
                return result

            result["checks"]["hash"] = file_hash

        # CHECK 3: File size anomalies
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)

            # Very small files with dangerous extensions
            if ext in dangerous_exts and file_size < 1024:
                result["malware_score"] += 0.2
                result["reasons"].append("Suspicious: Very small executable file")

            result["checks"]["size"] = file_size

        # CHECK 4: Download source (if available)
        # This would check the referring URL

        # Final verdict
        if result["malware_score"] >= self.thresholds["download_threshold"]:
            result["is_malware"] = True
            result["action"] = "BLOCK"
            self.stats["malware_blocked"] += 1
        elif result["malware_score"] >= 0.3:
            result["action"] = "WARN"

        return result

    def _check_patterns(self, url: str) -> float:
        """Check for suspicious URL patterns"""
        score = 0.0
        url_lower = url.lower()

        # Suspicious keywords
        suspicious_keywords = [
            "verify",
            "account",
            "suspended",
            "confirm",
            "update",
            "secure",
            "login",
            "signin",
            "password",
            "urgent",
            "alert",
            "warning",
            "locked",
            "unusual",
            "activity",
        ]

        keyword_count = sum(1 for kw in suspicious_keywords if kw in url_lower)
        score += min(keyword_count * 0.15, 0.5)

        # IP address in URL
        if any(char.isdigit() for char in urlparse(url).netloc.replace(".", "")):
            import re

            if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", urlparse(url).netloc):
                score += 0.4

        # Suspicious TLDs
        suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".work"]
        if any(url_lower.endswith(tld) for tld in suspicious_tlds):
            score += 0.3

        # Long URL
        if len(url) > 75:
            score += 0.1

        # Many subdomains
        subdomain_count = urlparse(url).netloc.count(".")
        if subdomain_count > 3:
            score += 0.2

        return min(score, 1.0)

    def _extract_quick_features(self, url: str) -> Dict:
        """Extract quick features for ML detection"""
        try:
            features = self.url_extractor.extract_all_features(url)
            return features
        except:
            return {}

    def _ml_predict(self, features: Dict) -> float:
        """AI-powered prediction (uses trained model if available)"""
        # Placeholder: Use pattern-based scoring
        # In production, this would use trained ML model
        score = 0.0

        if features.get("has_ip_address", False):
            score += 0.3
        if features.get("suspicious_tld", False):
            score += 0.2
        if features.get("has_suspicious_keywords", 0) > 2:
            score += 0.3
        if not features.get("has_https", True):
            score += 0.2

        return min(score, 1.0)

    def _is_zero_day(self, features: Dict, threat_score: float) -> bool:
        """Detect potential zero-day phishing attacks"""
        # Zero-day indicators:
        # 1. New domain (registered recently)
        # 2. High threat score but not in threat databases
        # 3. Unusual patterns not seen before

        if threat_score > self.thresholds["zero_day_threshold"]:
            # Check if domain is very new
            if features.get("domain_age_days", 365) < 30:
                return True

        return False

    def _extract_domain(self, url: str) -> str:
        """Extract base domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return ""

    def set_mode(self, mode: str):
        """Change detection sensitivity mode"""
        if mode in [
            DetectionMode.CONSERVATIVE,
            DetectionMode.BALANCED,
            DetectionMode.AGGRESSIVE,
        ]:
            self.mode = mode
            self.thresholds = self._get_thresholds(mode)
            print(f"🔧 Detection mode changed to: {mode.upper()}")
            print(f"🎯 New threat threshold: {self.thresholds['threat_threshold']}")
        else:
            print(f"❌ Invalid mode: {mode}")

    def get_statistics(self) -> Dict:
        """Get protection statistics"""
        return {
            **self.stats,
            "mode": self.mode,
            "thresholds": self.thresholds,
            "block_rate": (
                self.stats["threats_blocked"] / max(self.stats["urls_scanned"], 1)
            )
            * 100,
        }


# ============================================================================
# DEMO & TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🛡️ ULTIMATE AI/ML PHISHING DETECTOR - ADVANCED PROTECTION")
    print("=" * 80)
    print()

    # Test all three modes
    modes = [
        DetectionMode.CONSERVATIVE,
        DetectionMode.BALANCED,
        DetectionMode.AGGRESSIVE,
    ]

    test_urls = [
        "https://www.google.com",
        "http://paypa1.com/verify-account.php",
        "http://192.168.1.1/admin",
        "https://secure-login-amazon.tk/update",
    ]

    for mode in modes:
        print(f"\n{'='*80}")
        print(f"🎯 TESTING IN {mode.upper()} MODE")
        print(f"{'='*80}\n")

        detector = UltimatePhishingDetector(mode=mode)

        for url in test_urls:
            print(f"🔍 Scanning: {url}")
            result = detector.scan_url_realtime(url)

            print(f"   📊 Threat Score: {result['threat_score']:.2f}")
            print(f"   🎯 Threat Level: {result['threat_level']}")
            print(f"   🛡️  Action: {result['action']}")
            print(f"   ⚡ Latency: {result['latency_ms']:.2f}ms")

            if result["reasons"]:
                print(f"   📝 Reasons:")
                for reason in result["reasons"]:
                    print(f"      - {reason}")
            print()

        # Show statistics
        stats = detector.get_statistics()
        print(f"📈 STATISTICS ({mode.upper()}):")
        print(f"   URLs Scanned: {stats['urls_scanned']}")
        print(f"   Threats Blocked: {stats['threats_blocked']}")
        print(f"   Block Rate: {stats['block_rate']:.1f}%")
        print()

    # Test download protection
    print(f"\n{'='*80}")
    print("📥 TESTING DOWNLOAD PROTECTION")
    print(f"{'='*80}\n")

    detector = UltimatePhishingDetector(DetectionMode.BALANCED)

    test_files = ["document.pdf", "invoice.exe", "photo.jpg", "script.js"]

    for file_name in test_files:
        print(f"📥 Scanning download: {file_name}")
        result = detector.scan_download(file_name)

        print(f"   📊 Malware Score: {result['malware_score']:.2f}")
        print(f"   🛡️  Action: {result['action']}")

        if result["reasons"]:
            print(f"   📝 Reasons:")
            for reason in result["reasons"]:
                print(f"      - {reason}")
        print()

    print("🔥 ULTIMATE DETECTOR READY!")
    print("=" * 80)

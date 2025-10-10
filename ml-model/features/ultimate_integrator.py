"""
🚀 ULTIMATE FEATURE INTEGRATOR - 150+ FEATURES
===============================================

Combines ALL feature extractors into one HIGH-PERFORMANCE system
"""

import sys
import os
import numpy as np
from typing import Dict, List, Any

# Add features directory to path
sys.path.insert(0, os.path.dirname(__file__))

from url_features import URLFeatureExtractor
from ssl_features import SSLFeatureExtractor
from dns_features import DNSFeatureExtractor
from content_features import ContentFeatureExtractor
from behavioral_features import BehavioralFeatureExtractor
from network_features import NetworkFeatureExtractor


class UltimateFeatureIntegrator:
    """
    Ultimate Feature Integration System

    Combines 150+ features from 6 extractors:
    - URL Features (35)
    - SSL/TLS Features (25)
    - DNS Features (15)
    - Content Features (39)
    - Behavioral Features (25)
    - Network Features (20)

    Total: 159 FEATURES!
    """

    def __init__(self, timeout=5):
        print("🚀 Initializing Ultimate Feature Integrator...")

        # Initialize all extractors
        self.url_extractor = URLFeatureExtractor()
        self.ssl_extractor = SSLFeatureExtractor()
        self.dns_extractor = DNSFeatureExtractor()
        self.content_extractor = ContentFeatureExtractor()
        self.behavioral_extractor = BehavioralFeatureExtractor()
        self.network_extractor = NetworkFeatureExtractor(timeout=timeout)

        # Get feature names
        self.feature_names = self._get_all_feature_names()
        self.feature_count = len(self.feature_names)

        print(f"✅ Initialized with {self.feature_count} features!")

    def extract_all_features(
        self, url: str, html_content: str = None
    ) -> Dict[str, Any]:
        """
        Extract ALL 159 features from URL

        Args:
            url: URL to analyze
            html_content: Optional HTML content (for content features)

        Returns:
            Dictionary with all 159 features
        """
        all_features = {}

        try:
            # 1. URL Features (35)
            print(f"  Extracting URL features...")
            url_features = self.url_extractor.extract_all_features(url)
            all_features.update(url_features)

            # 2. SSL/TLS Features (25)
            print(f"  Extracting SSL features...")
            ssl_features = self.ssl_extractor.extract_all_features(url)
            all_features.update(ssl_features)

            # 3. DNS Features (15)
            print(f"  Extracting DNS features...")
            dns_features = self.dns_extractor.extract_all_features(url)
            all_features.update(dns_features)

            # 4. Content Features (39)
            print(f"  Extracting Content features...")
            content_features = self.content_extractor.extract_all_features(url)
            all_features.update(content_features)

            # 5. Behavioral Features (25)
            print(f"  Extracting Behavioral features...")
            behavioral_features = self.behavioral_extractor.extract_features(url)
            all_features.update(behavioral_features)

            # 6. Network Features (20)
            print(f"  Extracting Network features...")
            network_features = self.network_extractor.extract_features(url)
            all_features.update(network_features)

        except Exception as e:
            print(f"⚠️ Error extracting features: {e}")
            # Return defaults on error
            all_features = self._get_default_features()

        return all_features

    def extract_features_vector(self, url: str, html_content: str = None) -> np.ndarray:
        """
        Extract features as numpy vector (for ML models)

        Args:
            url: URL to analyze
            html_content: Optional HTML content

        Returns:
            Numpy array with 159 feature values
        """
        features_dict = self.extract_all_features(url, html_content)

        # Convert to ordered vector
        vector = []
        for name in self.feature_names:
            value = features_dict.get(name, 0)
            # Handle non-numeric values
            if isinstance(value, (int, float)):
                vector.append(value)
            else:
                vector.append(0)

        return np.array(vector, dtype=np.float32)

    def _get_all_feature_names(self) -> List[str]:
        """Get ordered list of ALL feature names"""
        all_names = []

        # URL features
        url_features = self.url_extractor.extract_all_features("http://example.com")
        all_names.extend(url_features.keys())

        # SSL features
        ssl_features = self.ssl_extractor._get_no_ssl_features()
        all_names.extend(ssl_features.keys())

        # DNS features
        dns_features = self.dns_extractor._get_default_features()
        all_names.extend(dns_features.keys())

        # Content features
        content_features = self.content_extractor._get_default_features()
        all_names.extend(content_features.keys())

        # Behavioral features
        behavioral_features = self.behavioral_extractor._get_default_features()
        all_names.extend(behavioral_features.keys())

        # Network features
        network_features = self.network_extractor._get_default_features()
        all_names.extend(network_features.keys())

        return all_names

    def _get_default_features(self) -> Dict[str, Any]:
        """Get default features from all extractors"""
        defaults = {}

        defaults.update(self.url_extractor.extract_all_features("http://example.com"))
        defaults.update(self.ssl_extractor._get_no_ssl_features())
        defaults.update(self.dns_extractor._get_default_features())
        defaults.update(self.content_extractor._get_default_features())
        defaults.update(self.behavioral_extractor._get_default_features())
        defaults.update(self.network_extractor._get_default_features())

        return defaults

    def get_feature_summary(self) -> Dict[str, int]:
        """Get feature count summary"""
        return {
            "URL Features": 35,
            "SSL/TLS Features": 25,
            "DNS Features": 15,
            "Content Features": 39,
            "Behavioral Features": 25,
            "Network Features": 20,
            "TOTAL": self.feature_count,
        }

    def print_feature_summary(self):
        """Print formatted feature summary"""
        print("\n" + "=" * 80)
        print("📊 ULTIMATE FEATURE INTEGRATOR - FEATURE SUMMARY")
        print("=" * 80)

        summary = self.get_feature_summary()
        for category, count in summary.items():
            if category == "TOTAL":
                print("-" * 80)
                print(f"{'🎯 ' + category:<50} {count:>10}")
            else:
                print(f"{category:<50} {count:>10}")

        print("=" * 80)


def demo_ultimate_integrator():
    """Demonstrate the ultimate feature integrator"""
    print("=" * 80)
    print("🚀 ULTIMATE FEATURE INTEGRATOR DEMO")
    print("=" * 80)

    # Initialize integrator
    integrator = UltimateFeatureIntegrator(timeout=5)

    # Print summary
    integrator.print_feature_summary()

    # Test URLs
    test_urls = [
        "https://google.com",
        "https://github.com",
    ]

    print(f"\n📊 Testing feature extraction...\n")

    for url in test_urls:
        print(f"\n{'=' * 80}")
        print(f"🔗 URL: {url}")
        print(f"{'=' * 80}\n")

        # Extract all features
        features = integrator.extract_all_features(url)

        # Get feature vector
        vector = integrator.extract_features_vector(url)

        print(f"\n📈 Results:")
        print(f"   Total Features Extracted: {len(features)}")
        print(f"   Feature Vector Shape: {vector.shape}")
        print(f"   Non-zero Features: {np.count_nonzero(vector)}")
        print(f"   Mean Value: {vector.mean():.2f}")
        print(f"   Max Value: {vector.max():.2f}")

        # Show sample features
        print(f"\n   Sample Features:")
        sample_keys = list(features.keys())[:10]
        for key in sample_keys:
            value = features[key]
            if isinstance(value, float):
                print(f"      {key}: {value:.2f}")
            else:
                print(f"      {key}: {value}")

        print(f"\n   ... and {len(features) - 10} more features")

    print("\n" + "=" * 80)
    print("✅ ULTIMATE FEATURE INTEGRATOR TEST COMPLETE!")
    print(f"   Successfully extracted {integrator.feature_count} features")
    print("=" * 80)


if __name__ == "__main__":
    demo_ultimate_integrator()

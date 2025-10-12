"""
Master Feature Extractor - Combines ALL Feature Modules
Extracts 150+ features in parallel for maximum performance
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from features.url_features import URLFeatureExtractor
from features.ssl_features import SSLFeatureExtractor
from features.dns_features import DNSFeatureExtractor
from features.content_features import ContentFeatureExtractor
from features.js_features import JSFeatureExtractor


class MasterFeatureExtractor:
    """
    Elite feature extractor combining all modules
    Extracts 150+ features with parallel processing for ultra-low latency
    """

    def __init__(self, parallel=True, max_workers=5):
        """
        Initialize all feature extractors

        Args:
            parallel: Enable parallel feature extraction
            max_workers: Number of parallel workers
        """
        self.url_extractor = URLFeatureExtractor()
        self.ssl_extractor = SSLFeatureExtractor()
        self.dns_extractor = DNSFeatureExtractor()
        self.content_extractor = ContentFeatureExtractor()
        self.js_extractor = JSFeatureExtractor()

        self.parallel = parallel
        self.max_workers = max_workers

        self.feature_count = {"url": 35, "ssl": 25, "dns": 15, "content": 40, "js": 28}

        self.total_features = sum(self.feature_count.values())

        print(f" Master Feature Extractor initialized")
        print(f" Total Features: {self.total_features}")
        print(f" Parallel Processing: {'Enabled' if parallel else 'Disabled'}")

    def extract_features(self, url: str, verbose=False) -> Dict[str, Any]:
        """
        Extract ALL features from a URL

        Args:
            url: URL to analyze
            verbose: Print timing information

        Returns:
            Dictionary with 150+ features
        """
        start_time = time.time()

        if self.parallel:
            features = self._extract_parallel(url)
        else:
            features = self._extract_sequential(url)

        # Add metadata
        features["url"] = url
        features["extraction_time_ms"] = int((time.time() - start_time) * 1000)

        if verbose:
            print(
                f" Extracted {len(features)} features in {features['extraction_time_ms']}ms"
            )

        return features

    def _extract_parallel(self, url: str) -> Dict[str, Any]:
        """Extract features in parallel using ThreadPoolExecutor"""
        features = {}

        # Define extraction tasks
        tasks = {
            "url": lambda: self.url_extractor.extract_all_features(url),
            "ssl": lambda: self.ssl_extractor.extract_all_features(url),
            "dns": lambda: self.dns_extractor.extract_all_features(url),
            "content": lambda: self.content_extractor.extract_all_features(url),
            "js": lambda: self.js_extractor.extract_all_features(url),
        }

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_name = {
                executor.submit(task): name for name, task in tasks.items()
            }

            # Collect results
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    result = future.result(timeout=30)
                    # Prefix feature names with module name
                    for key, value in result.items():
                        features[f"{name}_{key}"] = value
                except Exception as e:
                    print(f"Error in {name} extraction: {e}")
                    # Use default features on error
                    if name == "url":
                        result = self.url_extractor._get_default_features()
                    elif name == "ssl":
                        result = self.ssl_extractor._get_no_ssl_features()
                    elif name == "dns":
                        result = self.dns_extractor._get_default_features()
                    elif name == "content":
                        result = self.content_extractor._get_default_features()
                    elif name == "js":
                        result = self.js_extractor._get_default_features()

                    for key, value in result.items():
                        features[f"{name}_{key}"] = value

        return features

    def _extract_sequential(self, url: str) -> Dict[str, Any]:
        """Extract features sequentially (for debugging)"""
        features = {}

        # URL features
        url_features = self.url_extractor.extract_all_features(url)
        for key, value in url_features.items():
            features[f"url_{key}"] = value

        # SSL features
        ssl_features = self.ssl_extractor.extract_all_features(url)
        for key, value in ssl_features.items():
            features[f"ssl_{key}"] = value

        # DNS features
        dns_features = self.dns_extractor.extract_all_features(url)
        for key, value in dns_features.items():
            features[f"dns_{key}"] = value

        # Content features
        content_features = self.content_extractor.extract_all_features(url)
        for key, value in content_features.items():
            features[f"content_{key}"] = value

        # JS features
        js_features = self.js_extractor.extract_all_features(url)
        for key, value in js_features.items():
            features[f"js_{key}"] = value

        return features

    def extract_batch(self, urls: List[str], verbose=False) -> pd.DataFrame:
        """
        Extract features from multiple URLs

        Args:
            urls: List of URLs to analyze
            verbose: Print progress

        Returns:
            DataFrame with all features
        """
        print(f" Extracting features from {len(urls)} URLs...")

        all_features = []

        for i, url in enumerate(urls):
            if verbose and (i + 1) % 10 == 0:
                print(f"   Progress: {i + 1}/{len(urls)}")

            try:
                features = self.extract_features(url, verbose=False)
                all_features.append(features)
            except Exception as e:
                print(f"   Error processing {url}: {e}")
                continue

        df = pd.DataFrame(all_features)

        print(f" Extracted features from {len(df)} URLs successfully")
        print(f" Feature Matrix Shape: {df.shape}")

        return df

    def get_feature_names(self) -> List[str]:
        """Get all feature names in order"""
        feature_names = []

        # URL features
        for name in self.url_extractor.get_feature_names():
            feature_names.append(f"url_{name}")

        # SSL features
        for name in self.ssl_extractor.get_feature_names():
            feature_names.append(f"ssl_{name}")

        # DNS features
        for name in self.dns_extractor.get_feature_names():
            feature_names.append(f"dns_{name}")

        # Content features
        for name in self.content_extractor.get_feature_names():
            feature_names.append(f"content_{name}")

        # JS features
        for name in self.js_extractor.get_feature_names():
            feature_names.append(f"js_{name}")

        return feature_names

    def get_feature_summary(self) -> Dict[str, int]:
        """Get summary of feature counts by module"""
        return {
            "Total Features": self.total_features,
            "URL Features": self.feature_count["url"],
            "SSL Features": self.feature_count["ssl"],
            "DNS Features": self.feature_count["dns"],
            "Content Features": self.feature_count["content"],
            "JavaScript Features": self.feature_count["js"],
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    # Initialize master extractor
    extractor = MasterFeatureExtractor(parallel=True, max_workers=5)

    print("\n" + "=" * 80)
    print("MASTER FEATURE EXTRACTION TEST")
    print("=" * 80)

    # Print feature summary
    print("\n Feature Summary:")
    for module, count in extractor.get_feature_summary().items():
        print(f"   {module}: {count}")

    # Test URLs
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "http://suspicious-phishing-site.tk/login.php?verify=account",
    ]

    print(f"\n Testing {len(test_urls)} URLs...")
    print("=" * 80)

    for url in test_urls:
        print(f"\n URL: {url}")

        start = time.time()
        features = extractor.extract_features(url, verbose=True)
        elapsed = time.time() - start

        print(f"⏱  Total Time: {elapsed*1000:.2f}ms")
        print(f" Features Extracted: {len(features)}")

        # Show some key features
        print(f"\n   Key Indicators:")
        if "url_has_https" in features:
            print(f"   - HTTPS: {'Yes' if features['url_has_https'] else 'No'}")
        if "ssl_has_ssl" in features:
            print(f"   - SSL Certificate: {'Yes' if features['ssl_has_ssl'] else 'No'}")
        if "dns_domain_age_days" in features:
            print(f"   - Domain Age: {features['dns_domain_age_days']} days")
        if "content_form_count" in features:
            print(f"   - Forms: {features['content_form_count']}")
        if "js_total_obfuscation_indicators" in features:
            print(f"   - JS Obfuscation: {features['js_total_obfuscation_indicators']}")

        print("-" * 80)

    print("\n Master Feature Extraction Complete!")
    print("=" * 80)

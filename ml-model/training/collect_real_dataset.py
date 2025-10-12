#!/usr/bin/env python3
"""
 REAL-WORLD DATASET COLLECTION
Collects labeled phishing and legitimate URLs from trusted sources
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict
import pandas as pd
from datetime import datetime


class DatasetCollector:
    """Collects phishing and legitimate URLs from multiple sources"""

    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # PhishTank API
        self.phishtank_url = "http://data.phishtank.com/data/online-valid.json"

        # OpenPhish API
        self.openphish_url = "https://openphish.com/feed.txt"

        # Legitimate sites from Alexa/Tranco top sites
        self.tranco_url = "https://tranco-list.eu/top-1m.csv.zip"

    def collect_phishing_urls(self, limit: int = 10000) -> List[str]:
        """Collect phishing URLs from PhishTank and OpenPhish"""
        phishing_urls = []

        print(f" Collecting phishing URLs...")

        # 1. PhishTank
        try:
            print(f"   Fetching from PhishTank...")
            response = requests.get(self.phishtank_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                for entry in data[: limit // 2]:
                    if entry.get("verified") == "yes":
                        phishing_urls.append(entry["url"])
                print(f"    Collected {len(phishing_urls)} from PhishTank")
        except Exception as e:
            print(f"     PhishTank failed: {e}")

        # 2. OpenPhish
        try:
            print(f"   Fetching from OpenPhish...")
            response = requests.get(self.openphish_url, timeout=30)
            if response.status_code == 200:
                urls = response.text.strip().split("\n")
                phishing_urls.extend(urls[: limit // 2])
                print(f"    Collected {len(phishing_urls)} total phishing URLs")
        except Exception as e:
            print(f"     OpenPhish failed: {e}")

        return phishing_urls[:limit]

    def collect_legitimate_urls(self, limit: int = 10000) -> List[str]:
        """Collect legitimate URLs from trusted sources"""
        legitimate_urls = []

        print(f" Collecting legitimate URLs...")

        # Well-known legitimate sites
        trusted_domains = [
            # Tech companies
            "google.com",
            "microsoft.com",
            "apple.com",
            "amazon.com",
            "facebook.com",
            "twitter.com",
            "linkedin.com",
            "instagram.com",
            "youtube.com",
            "github.com",
            "stackoverflow.com",
            "reddit.com",
            "wikipedia.org",
            "medium.com",
            "netflix.com",
            # Financial institutions
            "chase.com",
            "bankofamerica.com",
            "wellsfargo.com",
            "paypal.com",
            "stripe.com",
            "coinbase.com",
            "robinhood.com",
            "fidelity.com",
            "schwab.com",
            "vanguard.com",
            # E-commerce
            "ebay.com",
            "walmart.com",
            "target.com",
            "bestbuy.com",
            "etsy.com",
            "shopify.com",
            "alibaba.com",
            "aliexpress.com",
            "wayfair.com",
            "overstock.com",
            # News & Media
            "cnn.com",
            "bbc.com",
            "nytimes.com",
            "washingtonpost.com",
            "reuters.com",
            "bloomberg.com",
            "wsj.com",
            "theguardian.com",
            "forbes.com",
            "techcrunch.com",
            # Education
            "mit.edu",
            "stanford.edu",
            "harvard.edu",
            "berkeley.edu",
            "oxford.ac.uk",
            "cambridge.org",
            "coursera.org",
            "udemy.com",
            "khanacademy.org",
            "edx.org",
            # Government
            "usa.gov",
            "irs.gov",
            "sec.gov",
            "fda.gov",
            "cdc.gov",
            "nasa.gov",
            "whitehouse.gov",
            "congress.gov",
            "nih.gov",
            "noaa.gov",
            # Cloud & Dev Tools
            "aws.amazon.com",
            "azure.microsoft.com",
            "cloud.google.com",
            "heroku.com",
            "digitalocean.com",
            "cloudflare.com",
            "mongodb.com",
            "docker.com",
            "kubernetes.io",
            # Productivity
            "zoom.us",
            "slack.com",
            "notion.so",
            "trello.com",
            "asana.com",
            "dropbox.com",
            "box.com",
            "evernote.com",
            "monday.com",
            "atlassian.com",
        ]

        # Add https:// prefix
        for domain in trusted_domains:
            legitimate_urls.append(f"https://{domain}")
            legitimate_urls.append(f"https://www.{domain}")

        print(f"    Collected {len(legitimate_urls)} legitimate URLs")

        # If we need more, add variations
        if len(legitimate_urls) < limit:
            additional = []
            for url in legitimate_urls[:100]:
                domain = url.replace("https://", "").replace("https://www.", "")
                additional.extend(
                    [
                        f"https://{domain}/about",
                        f"https://{domain}/contact",
                        f"https://{domain}/products",
                        f"https://{domain}/services",
                        f"https://{domain}/blog",
                    ]
                )
            legitimate_urls.extend(additional)

        return legitimate_urls[:limit]

    def create_balanced_dataset(
        self, num_phishing: int = 10000, num_legitimate: int = 10000
    ) -> pd.DataFrame:
        """Create a balanced dataset with equal phishing and legitimate URLs"""

        print(f"\n{'='*80}")
        print(f"COLLECTING REAL-WORLD DATASET")
        print(f"{'='*80}\n")

        # Collect URLs
        phishing_urls = self.collect_phishing_urls(num_phishing)
        legitimate_urls = self.collect_legitimate_urls(num_legitimate)

        # Create DataFrame
        df_phishing = pd.DataFrame(
            {
                "url": phishing_urls,
                "label": 1,  # 1 = phishing
                "source": "phishtank_openphish",
            }
        )

        df_legitimate = pd.DataFrame(
            {
                "url": legitimate_urls,
                "label": 0,  # 0 = legitimate
                "source": "trusted_domains",
            }
        )

        # Combine and shuffle
        df = pd.concat([df_phishing, df_legitimate], ignore_index=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        print(f"\n Dataset Statistics:")
        print(f"   Total URLs: {len(df)}")
        print(f"   Phishing: {len(df_phishing)} ({len(df_phishing)/len(df)*100:.1f}%)")
        print(
            f"   Legitimate: {len(df_legitimate)} ({len(df_legitimate)/len(df)*100:.1f}%)"
        )

        return df

    def save_dataset(self, df: pd.DataFrame, filename: str = None):
        """Save dataset to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phishing_dataset_{timestamp}.csv"

        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)

        print(f"\n Dataset saved to: {filepath}")
        print(f"   Size: {filepath.stat().st_size / 1024 / 1024:.2f} MB")

        return filepath


def main():
    collector = DatasetCollector(output_dir="ml-model/datasets")

    # Collect 10,000 of each
    df = collector.create_balanced_dataset(num_phishing=10000, num_legitimate=10000)

    # Save dataset
    filepath = collector.save_dataset(df, "real_world_dataset.csv")

    print(f"\n Dataset collection complete!")
    print(f"\nNext steps:")
    print(f"1. Extract 159 features: python extract_features_parallel.py")
    print(f"2. Train models: python train_with_real_data.py")


if __name__ == "__main__":
    main()

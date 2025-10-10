"""
Data Collector - Fetch training data from multiple sources
Collects phishing and legitimate URLs from PhishTank, OpenPhish, and Alexa
"""

import pandas as pd
import requests
from pathlib import Path
import zipfile
import io
from datetime import datetime
from typing import List, Dict
import time
import sys

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import RAW_DATA_DIR, DATA_SOURCES


class DataCollector:
    """Collect phishing and legitimate URLs for training"""

    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

        print("✅ Data Collector initialized")
        print(f"📁 Raw data directory: {self.raw_data_dir}")

    def collect_phishtank(self, limit: int = None) -> pd.DataFrame:
        """
        Collect phishing URLs from PhishTank

        Args:
            limit: Maximum number of URLs to collect

        Returns:
            DataFrame with phishing URLs
        """
        print("\n📥 Collecting from PhishTank...")

        try:
            url = DATA_SOURCES["phishtank"]["url"]

            print(f"   Downloading from: {url}")
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                # Save raw data
                output_file = self.raw_data_dir / "phishtank_raw.csv"
                with open(output_file, "wb") as f:
                    f.write(response.content)

                # Parse CSV
                df = pd.read_csv(io.StringIO(response.text))

                # Extract URLs
                if "url" in df.columns:
                    phishing_urls = df["url"].tolist()
                else:
                    print("   ⚠️  'url' column not found, using first column")
                    phishing_urls = df.iloc[:, 0].tolist()

                # Limit if specified
                if limit:
                    phishing_urls = phishing_urls[:limit]

                # Create DataFrame
                result_df = pd.DataFrame(
                    {
                        "url": phishing_urls,
                        "label": 1,  # 1 = phishing
                        "source": "phishtank",
                        "collected_date": datetime.now().isoformat(),
                    }
                )

                print(f"   ✅ Collected {len(result_df)} phishing URLs from PhishTank")
                return result_df

        except Exception as e:
            print(f"   ❌ Error collecting from PhishTank: {e}")
            return pd.DataFrame(columns=["url", "label", "source", "collected_date"])

    def collect_openphish(self, limit: int = None) -> pd.DataFrame:
        """
        Collect phishing URLs from OpenPhish

        Args:
            limit: Maximum number of URLs to collect

        Returns:
            DataFrame with phishing URLs
        """
        print("\n📥 Collecting from OpenPhish...")

        try:
            url = DATA_SOURCES["openphish"]["url"]

            print(f"   Downloading from: {url}")
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                # Save raw data
                output_file = self.raw_data_dir / "openphish_raw.txt"
                with open(output_file, "wb") as f:
                    f.write(response.content)

                # Parse URLs (one per line)
                urls = response.text.strip().split("\n")
                urls = [u.strip() for u in urls if u.strip()]

                # Limit if specified
                if limit:
                    urls = urls[:limit]

                # Create DataFrame
                result_df = pd.DataFrame(
                    {
                        "url": urls,
                        "label": 1,  # 1 = phishing
                        "source": "openphish",
                        "collected_date": datetime.now().isoformat(),
                    }
                )

                print(f"   ✅ Collected {len(result_df)} phishing URLs from OpenPhish")
                return result_df

        except Exception as e:
            print(f"   ❌ Error collecting from OpenPhish: {e}")
            return pd.DataFrame(columns=["url", "label", "source", "collected_date"])

    def collect_alexa_top(self, sample_size: int = 10000) -> pd.DataFrame:
        """
        Collect legitimate URLs from Alexa Top sites

        Args:
            sample_size: Number of top sites to collect

        Returns:
            DataFrame with legitimate URLs
        """
        print(f"\n📥 Collecting top {sample_size} sites from Alexa...")

        try:
            # Note: Alexa Top Million is no longer freely available
            # Using alternative: Tranco list (similar to Alexa)
            url = "https://tranco-list.eu/top-1m.csv.zip"

            print(f"   Downloading from: {url}")
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                # Extract ZIP
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # Read CSV from ZIP
                    with z.open(z.namelist()[0]) as f:
                        df = pd.read_csv(f, header=None, names=["rank", "domain"])

                # Take top N sites
                top_domains = df.head(sample_size)["domain"].tolist()

                # Add https://www. prefix
                urls = [f"https://www.{domain}" for domain in top_domains]

                # Save raw data
                output_file = self.raw_data_dir / "alexa_raw.csv"
                pd.DataFrame({"url": urls}).to_csv(output_file, index=False)

                # Create DataFrame
                result_df = pd.DataFrame(
                    {
                        "url": urls,
                        "label": 0,  # 0 = legitimate
                        "source": "alexa_top",
                        "collected_date": datetime.now().isoformat(),
                    }
                )

                print(f"   ✅ Collected {len(result_df)} legitimate URLs")
                return result_df

        except Exception as e:
            print(f"   ❌ Error collecting from Alexa: {e}")

            # Fallback: Use common legitimate domains
            print("   ℹ️  Using fallback list of known legitimate domains")
            legitimate_domains = self._get_fallback_legitimate_domains(sample_size)

            result_df = pd.DataFrame(
                {
                    "url": legitimate_domains,
                    "label": 0,
                    "source": "fallback",
                    "collected_date": datetime.now().isoformat(),
                }
            )

            return result_df

    def _get_fallback_legitimate_domains(self, count: int) -> List[str]:
        """Get list of known legitimate domains as fallback"""
        domains = [
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
            "pinterest.com",
            "ebay.com",
            "cnn.com",
            "bbc.com",
            "nytimes.com",
            "espn.com",
            "craigslist.org",
            "imdb.com",
            "wordpress.com",
            "adobe.com",
            "paypal.com",
            "dropbox.com",
            "twitch.tv",
            "bing.com",
            "office.com",
        ]

        # Repeat if needed to reach count
        while len(domains) < count:
            domains.extend(domains[: count - len(domains)])

        return [f"https://www.{d}" for d in domains[:count]]

    def collect_all(
        self, phishing_count: int = 25000, legitimate_count: int = 25000
    ) -> pd.DataFrame:
        """
        Collect phishing and legitimate URLs from all sources

        Args:
            phishing_count: Number of phishing URLs to collect
            legitimate_count: Number of legitimate URLs to collect

        Returns:
            Combined DataFrame with all URLs
        """
        print("\n" + "=" * 80)
        print("DATA COLLECTION STARTED")
        print("=" * 80)
        print(f"Target: {phishing_count} phishing + {legitimate_count} legitimate URLs")

        all_dataframes = []

        # Collect phishing URLs
        print("\n🎣 Collecting Phishing URLs...")
        print("-" * 80)

        # PhishTank
        df_phishtank = self.collect_phishtank(limit=phishing_count // 2)
        if not df_phishtank.empty:
            all_dataframes.append(df_phishtank)

        time.sleep(2)  # Be nice to servers

        # OpenPhish
        df_openphish = self.collect_openphish(limit=phishing_count // 2)
        if not df_openphish.empty:
            all_dataframes.append(df_openphish)

        # Collect legitimate URLs
        print("\n✅ Collecting Legitimate URLs...")
        print("-" * 80)

        df_legitimate = self.collect_alexa_top(sample_size=legitimate_count)
        if not df_legitimate.empty:
            all_dataframes.append(df_legitimate)

        # Combine all
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)

            # Remove duplicates
            before_dedup = len(combined_df)
            combined_df = combined_df.drop_duplicates(subset=["url"], keep="first")
            after_dedup = len(combined_df)

            if before_dedup != after_dedup:
                print(f"\n   ℹ️  Removed {before_dedup - after_dedup} duplicate URLs")

            # Save combined dataset
            output_file = self.raw_data_dir / "combined_dataset.csv"
            combined_df.to_csv(output_file, index=False)

            # Print statistics
            print("\n" + "=" * 80)
            print("DATA COLLECTION COMPLETE")
            print("=" * 80)
            print(f"📊 Total URLs: {len(combined_df)}")
            print(f"   🎣 Phishing: {len(combined_df[combined_df['label'] == 1])}")
            print(f"   ✅ Legitimate: {len(combined_df[combined_df['label'] == 0])}")
            print(f"📁 Saved to: {output_file}")

            return combined_df
        else:
            print("\n❌ No data collected!")
            return pd.DataFrame()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    collector = DataCollector()

    # Collect dataset
    # For testing, use smaller numbers
    df = collector.collect_all(
        phishing_count=100,  # Collect 100 phishing URLs for testing
        legitimate_count=100,  # Collect 100 legitimate URLs for testing
    )

    if not df.empty:
        print("\n📋 Sample Data:")
        print(df.head(10))

        print("\n📊 Label Distribution:")
        print(df["label"].value_counts())

#!/usr/bin/env python3
"""
 PARALLEL FEATURE EXTRACTION - SUPER MAXIMUM PERFORMANCE
Extracts 159 features from URLs using parallel processing and optimization
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import sys
import time
from tqdm import tqdm
import pickle

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from deployment.production_feature_extractor import ProductionFeatureExtractor


class ParallelFeatureExtractor:
    """Extracts features in parallel for maximum performance"""

    def __init__(self, n_workers: int = None, use_cache: bool = True):
        """
        Args:
            n_workers: Number of parallel workers (default: CPU count)
            use_cache: Enable feature caching to avoid re-extraction
        """
        self.n_workers = n_workers or mp.cpu_count()
        self.use_cache = use_cache
        self.cache_file = Path("ml-model/datasets/feature_cache.pkl")
        self.feature_cache = self._load_cache()

        print(f" Initialized with {self.n_workers} workers")

    def _load_cache(self) -> Dict:
        """Load cached features"""
        if self.use_cache and self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    cache = pickle.load(f)
                print(f" Loaded {len(cache)} cached features")
                return cache
            except:
                pass
        return {}

    def _save_cache(self):
        """Save feature cache"""
        if self.use_cache:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.feature_cache, f)
            print(f" Saved {len(self.feature_cache)} features to cache")

    def extract_single_url(self, url: str) -> Dict:
        """Extract features for a single URL"""
        # Check cache first
        if url in self.feature_cache:
            return self.feature_cache[url]

        try:
            extractor = ProductionFeatureExtractor()
            features = extractor.extract_features(url)

            # Cache the result
            self.feature_cache[url] = features

            return features
        except Exception as e:
            print(f" Error extracting features for {url}: {e}")
            return None

    def extract_batch(self, urls: List[str], batch_size: int = 100) -> pd.DataFrame:
        """
        Extract features for a batch of URLs in parallel

        Args:
            urls: List of URLs to process
            batch_size: Number of URLs to process in each batch

        Returns:
            DataFrame with extracted features
        """
        print(f"\n{'='*80}")
        print(f"EXTRACTING FEATURES FOR {len(urls)} URLs")
        print(f"{'='*80}\n")
        print(f"  Workers: {self.n_workers}")
        print(f" Batch size: {batch_size}")
        print(f" Cache enabled: {self.use_cache}")

        all_features = []
        failed_urls = []

        start_time = time.time()

        # Process in batches to show progress
        with tqdm(total=len(urls), desc="Extracting features") as pbar:
            with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
                # Submit all URLs
                future_to_url = {
                    executor.submit(self.extract_single_url, url): url for url in urls
                }

                # Process completed futures
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        features = future.result(timeout=30)
                        if features:
                            features["url"] = url
                            all_features.append(features)
                        else:
                            failed_urls.append(url)
                    except Exception as e:
                        failed_urls.append(url)
                        print(f"\n Failed: {url} - {e}")

                    pbar.update(1)

                    # Save cache periodically
                    if len(all_features) % 100 == 0:
                        self._save_cache()

        elapsed = time.time() - start_time

        # Final cache save
        self._save_cache()

        # Create DataFrame
        df = pd.DataFrame(all_features)

        # Print statistics
        print(f"\n{'='*80}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*80}")
        print(
            f" Successfully extracted: {len(all_features)}/{len(urls)} ({len(all_features)/len(urls)*100:.1f}%)"
        )
        print(f" Failed: {len(failed_urls)}")
        print(f"⏱  Total time: {elapsed:.2f}s")
        print(f" Average time per URL: {elapsed/len(urls):.2f}s")
        print(f" URLs per second: {len(urls)/elapsed:.2f}")

        if failed_urls:
            print(f"\n  Failed URLs ({len(failed_urls)}):")
            for url in failed_urls[:10]:
                print(f"   - {url}")
            if len(failed_urls) > 10:
                print(f"   ... and {len(failed_urls)-10} more")

        return df

    def extract_from_csv(
        self,
        input_file: str,
        output_file: str = None,
        url_column: str = "url",
        label_column: str = "label",
    ) -> pd.DataFrame:
        """
        Extract features from URLs in a CSV file

        Args:
            input_file: Path to input CSV with URLs
            output_file: Path to save features (default: auto-generated)
            url_column: Name of column containing URLs
            label_column: Name of column containing labels

        Returns:
            DataFrame with extracted features and labels
        """
        # Load URLs
        print(f" Loading URLs from {input_file}")
        df_input = pd.read_csv(input_file)
        print(f"   Found {len(df_input)} URLs")

        # Extract features
        df_features = self.extract_batch(df_input[url_column].tolist())

        # Merge with labels
        df_result = df_features.merge(
            df_input[[url_column, label_column]],
            left_on="url",
            right_on=url_column,
            how="left",
        )

        # Save to file
        if output_file is None:
            input_path = Path(input_file)
            output_file = input_path.parent / f"{input_path.stem}_features.csv"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_result.to_csv(output_path, index=False)

        print(f"\n Features saved to: {output_path}")
        print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"   Rows: {len(df_result)}")
        print(f"   Columns: {len(df_result.columns)}")

        return df_result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract features in parallel")
    parser.add_argument("--input", required=True, help="Input CSV file with URLs")
    parser.add_argument("--output", help="Output CSV file for features")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")

    args = parser.parse_args()

    # Create extractor
    extractor = ParallelFeatureExtractor(
        n_workers=args.workers, use_cache=not args.no_cache
    )

    # Extract features
    df = extractor.extract_from_csv(input_file=args.input, output_file=args.output)

    print(f"\n Feature extraction complete!")
    print(f"\nNext step: python train_with_real_data.py")


if __name__ == "__main__":
    main()

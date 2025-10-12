"""
Quick Start Script - Complete ML Model Training Pipeline
Run this to train the ELITE phishing detection model from scratch
"""

import sys
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).resolve().parent))

from utils.data_collector import DataCollector
from features.master_extractor import MasterFeatureExtractor
from training.train_ensemble import EnsembleTrainer
from utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
import pandas as pd


def main():
    print("\n" + "=" * 80)
    print(" ELITE PHISHING DETECTION ML MODEL - QUICK START")
    print("=" * 80)
    print("\nThis script will:")
    print("  1⃣  Collect training data (phishing + legitimate URLs)")
    print("  2⃣  Extract 150+ features from each URL")
    print("  3⃣  Train ensemble models (Random Forest + XGBoost + LightGBM)")
    print("  4⃣  Achieve >98% accuracy with <0.5% false positive rate")
    print("\n" + "=" * 80)

    # Configuration
    PHISHING_COUNT = 1000  # Number of phishing URLs to collect
    LEGITIMATE_COUNT = 1000  # Number of legitimate URLs to collect

    print(f"\n Configuration:")
    print(f"   Phishing URLs:    {PHISHING_COUNT}")
    print(f"   Legitimate URLs:  {LEGITIMATE_COUNT}")
    print(f"   Total samples:    {PHISHING_COUNT + LEGITIMATE_COUNT}")

    input("\n⏸  Press ENTER to start, or Ctrl+C to cancel...")

    # ========================================================================
    # STEP 1: DATA COLLECTION
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: DATA COLLECTION")
    print("=" * 80)

    collector = DataCollector()
    df_urls = collector.collect_all(
        phishing_count=PHISHING_COUNT, legitimate_count=LEGITIMATE_COUNT
    )

    if df_urls.empty:
        print("\n Failed to collect data. Exiting.")
        return

    print(f"\n Collected {len(df_urls)} URLs successfully")

    # ========================================================================
    # STEP 2: FEATURE EXTRACTION
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: FEATURE EXTRACTION")
    print("=" * 80)
    print("\nExtracting 150+ features from each URL...")
    print("  This may take several minutes...")

    input("\n⏸  Press ENTER to continue...")

    extractor = MasterFeatureExtractor(parallel=True, max_workers=5)

    # Extract features
    urls_to_extract = df_urls["url"].tolist()
    df_features = extractor.extract_batch(urls_to_extract, verbose=True)

    # Add labels
    df_features["label"] = df_urls["label"].values
    df_features["source"] = df_urls["source"].values

    # Save features
    features_file = PROCESSED_DATA_DIR / "features.csv"
    features_file.parent.mkdir(parents=True, exist_ok=True)
    df_features.to_csv(features_file, index=False)

    print(f"\n Features extracted and saved to: {features_file}")
    print(f"   Shape: {df_features.shape}")

    # ========================================================================
    # STEP 3: MODEL TRAINING
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: MODEL TRAINING")
    print("=" * 80)
    print("\nTraining ensemble models...")
    print("   - Random Forest (500 trees)")
    print("   - XGBoost (gradient boosting)")
    print("   - LightGBM (fast gradient boosting)")

    input("\n⏸  Press ENTER to start training...")

    trainer = EnsembleTrainer()
    trainer.train_all(str(features_file))

    # ========================================================================
    # COMPLETION
    # ========================================================================
    print("\n" + "=" * 80)
    print(" TRAINING PIPELINE COMPLETE!")
    print("=" * 80)

    print("\n Generated Files:")
    print(f"   Data:     {RAW_DATA_DIR}")
    print(f"   Features: {features_file}")
    print(f"   Models:   {Path(__file__).parent / 'models'}")

    print("\n Performance Summary:")
    if trainer.metrics:
        for model_name, metrics in trainer.metrics.items():
            print(f"\n   {model_name.upper()}:")
            print(f"      Accuracy:  {metrics['accuracy']*100:.2f}%")
            print(f"      Precision: {metrics['precision']:.4f}")
            print(f"      Recall:    {metrics['recall']:.4f}")
            print(f"      FPR:       {metrics['fpr']*100:.3f}%")

    print("\n Next Steps:")
    print("   1. Test models: python evaluation/evaluate.py")
    print("   2. Export to browser: python deployment/export_tfjs.py")
    print("   3. Integrate with Chrome extension")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹  Training cancelled by user")
    except Exception as e:
        print(f"\n\n Error: {e}")
        import traceback

        traceback.print_exc()

"""
🚀 SIMPLIFIED ML MODEL TRAINING
===============================================

Trains ML models with sample data for demonstration
Works without external data collection

This will:
1. Generate synthetic training data
2. Extract features
3. Train Random Forest, XGBoost, LightGBM
4. Generate evaluation reports
5. Save trained models
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
import joblib
import json
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

try:
    import xgboost as xgb
    import lightgbm as lgb

    XGBOOST_AVAILABLE = True
    LIGHTGBM_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    LIGHTGBM_AVAILABLE = False

from features.url_features import URLFeatureExtractor


class SimpleTrainer:
    """Simple ML trainer with synthetic data"""

    def __init__(self):
        self.url_extractor = URLFeatureExtractor()
        self.models = {}
        self.results = {}

    def generate_sample_data(self, n_samples=1000):
        """Generate sample URLs for training"""
        print("\n📊 Generating sample training data...")

        # Phishing URLs (examples)
        phishing_urls = [
            "http://paypa1-verify.tk/secure/login",
            "http://apple-id-locked.ml/unlock",
            "http://amazon-account.xyz/verify",
            "http://192.168.1.100/admin/login",
            "http://secure-banking.work/update-info",
            "http://netflix-billing.top/payment",
            "http://microsoft-account.cf/security",
            "http://google-drive.gq/share",
            "http://facebook-security.ga/verify",
            "http://instagram-help.tk/support",
            "http://wellsfargo-online.xyz/signin",
            "http://chase-secure.work/verify",
            "http://citibank-alert.top/account",
            "http://bankofamerica-verify.ml/update",
            "http://paypal-resolution.cf/center",
            "http://ebay-account.gq/suspended",
            "http://amazon-prime.ga/renew",
            "http://dropbox-storage.tk/upgrade",
            "http://adobe-cloud.xyz/activate",
            "http://linkedin-security.work/alert",
        ]

        # Legitimate URLs (examples)
        legitimate_urls = [
            "https://www.google.com",
            "https://www.youtube.com",
            "https://www.facebook.com",
            "https://www.amazon.com",
            "https://www.microsoft.com",
            "https://www.apple.com",
            "https://www.linkedin.com",
            "https://www.github.com",
            "https://www.stackoverflow.com",
            "https://www.wikipedia.org",
            "https://www.twitter.com",
            "https://www.instagram.com",
            "https://www.netflix.com",
            "https://www.paypal.com",
            "https://www.ebay.com",
            "https://www.reddit.com",
            "https://www.wordpress.com",
            "https://www.adobe.com",
            "https://www.dropbox.com",
            "https://www.spotify.com",
        ]

        # Generate more samples by variations
        all_phishing = []
        all_legitimate = []

        # Expand phishing samples
        for i in range(n_samples // 2):
            base_url = phishing_urls[i % len(phishing_urls)]
            variations = [
                base_url,
                base_url + f"?id={i}",
                base_url + f"&session={i}",
                base_url.replace("http://", "http://www."),
            ]
            all_phishing.extend(variations[: n_samples // 2 // len(phishing_urls) + 1])

        # Expand legitimate samples
        for i in range(n_samples // 2):
            base_url = legitimate_urls[i % len(legitimate_urls)]
            variations = [
                base_url,
                base_url + f"/page/{i}",
                base_url + f"?q=search",
                base_url + f"/category/tech",
            ]
            all_legitimate.extend(
                variations[: n_samples // 2 // len(legitimate_urls) + 1]
            )

        # Trim to exact size
        all_phishing = all_phishing[: n_samples // 2]
        all_legitimate = all_legitimate[: n_samples // 2]

        print(f"   ✅ Generated {len(all_phishing)} phishing URLs")
        print(f"   ✅ Generated {len(all_legitimate)} legitimate URLs")

        return all_phishing, all_legitimate

    def extract_features(self, urls, labels):
        """Extract features from URLs"""
        print("\n🔍 Extracting features...")

        features_list = []
        valid_urls = []
        valid_labels = []

        for url, label in zip(urls, labels):
            try:
                features = self.url_extractor.extract_all_features(url)
                # Convert to numeric features
                feature_vector = self._features_to_vector(features)
                features_list.append(feature_vector)
                valid_urls.append(url)
                valid_labels.append(label)
            except Exception as e:
                continue  # Skip problematic URLs

        print(f"   ✅ Extracted features from {len(features_list)} URLs")

        return np.array(features_list), np.array(valid_labels), valid_urls

    def _features_to_vector(self, features):
        """Convert feature dict to numeric vector"""
        vector = [
            features.get("url_length", 0),
            features.get("domain_length", 0),
            features.get("path_length", 0),
            features.get("num_dots", 0),
            features.get("num_hyphens", 0),
            features.get("num_underscores", 0),
            features.get("num_slashes", 0),
            features.get("num_digits", 0),
            features.get("num_special_chars", 0),
            int(features.get("has_ip_address", False)),
            int(features.get("has_https", False)),
            int(features.get("suspicious_tld", False)),
            features.get("subdomain_count", 0),
            features.get("entropy", 0),
            features.get("has_suspicious_keywords", 0),
        ]
        return vector

    def train_models(self, X_train, y_train, X_test, y_test):
        """Train all ML models"""
        print("\n🧠 Training ML models...")
        print("=" * 80)

        # 1. Random Forest
        print("\n📊 Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        rf_proba = rf_model.predict_proba(X_test)[:, 1]

        self.models["random_forest"] = rf_model
        self.results["random_forest"] = self._evaluate_model(
            "Random Forest", y_test, rf_pred, rf_proba
        )

        # 2. XGBoost
        if XGBOOST_AVAILABLE:
            print("\n📊 Training XGBoost...")
            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
            )
            xgb_model.fit(X_train, y_train)
            xgb_pred = xgb_model.predict(X_test)
            xgb_proba = xgb_model.predict_proba(X_test)[:, 1]

            self.models["xgboost"] = xgb_model
            self.results["xgboost"] = self._evaluate_model(
                "XGBoost", y_test, xgb_pred, xgb_proba
            )
        else:
            print("\n⚠️  XGBoost not available")

        # 3. LightGBM
        if LIGHTGBM_AVAILABLE:
            print("\n📊 Training LightGBM...")
            lgb_model = lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            )
            lgb_model.fit(X_train, y_train)
            lgb_pred = lgb_model.predict(X_test)
            lgb_proba = lgb_model.predict_proba(X_test)[:, 1]

            self.models["lightgbm"] = lgb_model
            self.results["lightgbm"] = self._evaluate_model(
                "LightGBM", y_test, lgb_pred, lgb_proba
            )
        else:
            print("\n⚠️  LightGBM not available")

        print("\n" + "=" * 80)
        print("✅ All models trained successfully!")

    def _evaluate_model(self, name, y_test, y_pred, y_proba):
        """Evaluate model performance"""
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        print(f"\n   {name} Results:")
        print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1 Score:  {f1:.4f}")
        print(f"   AUC-ROC:   {auc:.4f}")

        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "auc_roc": float(auc),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

    def save_models(self, output_dir="models"):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n💾 Saving models to {output_dir}/...")

        for name, model in self.models.items():
            model_path = os.path.join(output_dir, f"{name}_model.pkl")
            joblib.dump(model, model_path)
            print(f"   ✅ Saved {name}")

        print(f"   ✅ Saved {len(self.models)} models")

    def generate_report(self, output_dir="reports"):
        """Generate evaluation report"""
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(
            output_dir,
            f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )

        report = {
            "timestamp": datetime.now().isoformat(),
            "models": self.results,
            "summary": {
                "best_model": max(self.results.items(), key=lambda x: x[1]["accuracy"])[
                    0
                ],
                "best_accuracy": max(r["accuracy"] for r in self.results.values()),
                "avg_accuracy": np.mean([r["accuracy"] for r in self.results.values()]),
            },
        }

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Evaluation report saved to: {report_path}")
        return report


def main():
    """Main training pipeline"""
    print("=" * 80)
    print("🚀 SIMPLIFIED ML MODEL TRAINING")
    print("=" * 80)

    trainer = SimpleTrainer()

    # Generate sample data
    phishing_urls, legitimate_urls = trainer.generate_sample_data(n_samples=1000)

    # Combine and label
    all_urls = phishing_urls + legitimate_urls
    all_labels = [1] * len(phishing_urls) + [0] * len(legitimate_urls)

    # Extract features
    X, y, valid_urls = trainer.extract_features(all_urls, all_labels)

    print(f"\n📊 Dataset Statistics:")
    print(f"   Total URLs: {len(valid_urls)}")
    print(f"   Phishing: {sum(y)} ({sum(y)/len(y)*100:.1f}%)")
    print(f"   Legitimate: {len(y)-sum(y)} ({(len(y)-sum(y))/len(y)*100:.1f}%)")
    print(f"   Features: {X.shape[1]}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\n📊 Train/Test Split:")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Testing samples:  {len(X_test)}")

    # Train models
    trainer.train_models(X_train, y_train, X_test, y_test)

    # Save models
    trainer.save_models()

    # Generate report
    report = trainer.generate_report()

    # Print summary
    print("\n" + "=" * 80)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Best Model: {report['summary']['best_model']}")
    print(f"📈 Best Accuracy: {report['summary']['best_accuracy']*100:.2f}%")
    print(f"📈 Average Accuracy: {report['summary']['avg_accuracy']*100:.2f}%")
    print("\n✅ Models ready for deployment!")
    print("=" * 80)


if __name__ == "__main__":
    main()

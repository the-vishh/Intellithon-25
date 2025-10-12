"""
Elite Ensemble Model Training Pipeline
Trains Random Forest, XGBoost, and LightGBM with hyperparameter tuning
Target: >98% accuracy, <0.5% false positive rate
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
import xgboost as xgb
import lightgbm as lgb
import joblib
from pathlib import Path
import sys
import time
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import (
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    TRAIN_CONFIG,
    RANDOM_FOREST_PARAMS,
    XGBOOST_PARAMS,
    LIGHTGBM_PARAMS,
)


class EnsembleTrainer:
    """Train ensemble of elite phishing detection models"""

    def __init__(self):
        self.models_dir = MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.metrics = {}

        print(" Ensemble Trainer initialized")

    def load_data(self, features_file: str) -> tuple:
        """
        Load and prepare training data

        Args:
            features_file: Path to CSV file with extracted features

        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        print("\n Loading training data...")

        # Load features
        df = pd.read_csv(features_file)
        print(f"   Loaded {len(df)} samples")

        # Separate features and labels
        if "label" not in df.columns:
            raise ValueError("Dataset must have 'label' column")

        # Remove non-feature columns
        non_feature_cols = [
            "url",
            "label",
            "source",
            "collected_date",
            "extraction_time_ms",
        ]
        X = df.drop(columns=[col for col in non_feature_cols if col in df.columns])
        y = df["label"]

        self.feature_names = X.columns.tolist()

        print(f"   Features: {X.shape[1]}")
        print(f"   Samples: {len(X)}")
        print(f"   Phishing: {sum(y == 1)} ({sum(y == 1)/len(y)*100:.1f}%)")
        print(f"   Legitimate: {sum(y == 0)} ({sum(y == 0)/len(y)*100:.1f}%)")

        # Handle missing values
        print("\n Preprocessing data...")
        X = X.fillna(0)

        # Replace infinite values
        X = X.replace([np.inf, -np.inf], 0)

        # Split data: 70% train, 15% validation, 15% test
        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=0.30,
            random_state=TRAIN_CONFIG["random_state"],
            stratify=y if TRAIN_CONFIG["stratify"] else None,
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=0.50,
            random_state=TRAIN_CONFIG["random_state"],
            stratify=y_temp if TRAIN_CONFIG["stratify"] else None,
        )

        print(f"   Train: {len(X_train)} samples")
        print(f"   Val:   {len(X_val)} samples")
        print(f"   Test:  {len(X_test)} samples")

        # Scale features
        print("\n Scaling features...")
        scaler = RobustScaler()  # Robust to outliers
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)

        self.scalers["robust"] = scaler

        # Save scaler
        scaler_file = self.models_dir / "scaler.joblib"
        joblib.dump(scaler, scaler_file)
        print(f"    Scaler saved to {scaler_file}")

        return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test

    def train_random_forest(
        self, X_train, y_train, X_val, y_val
    ) -> RandomForestClassifier:
        """Train Random Forest model"""
        print("\n" + "=" * 80)
        print(" TRAINING RANDOM FOREST")
        print("=" * 80)

        start_time = time.time()

        # Initialize model
        rf_model = RandomForestClassifier(**RANDOM_FOREST_PARAMS)

        print("   Hyperparameters:")
        for key, value in RANDOM_FOREST_PARAMS.items():
            print(f"      {key}: {value}")

        # Train
        print("\n   Training...")
        rf_model.fit(X_train, y_train)

        # Evaluate on validation set
        y_pred = rf_model.predict(X_val)
        y_pred_proba = rf_model.predict_proba(X_val)[:, 1]

        metrics = self._calculate_metrics(y_val, y_pred, y_pred_proba, "Random Forest")
        self.metrics["random_forest"] = metrics

        training_time = time.time() - start_time
        print(f"\n   ⏱  Training time: {training_time:.2f}s")

        # Save model
        model_file = self.models_dir / "random_forest" / "model.joblib"
        model_file.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(rf_model, model_file)
        print(f"    Model saved to {model_file}")

        self.models["random_forest"] = rf_model
        return rf_model

    def train_xgboost(self, X_train, y_train, X_val, y_val) -> xgb.XGBClassifier:
        """Train XGBoost model"""
        print("\n" + "=" * 80)
        print(" TRAINING XGBOOST")
        print("=" * 80)

        start_time = time.time()

        # Initialize model
        xgb_model = xgb.XGBClassifier(**XGBOOST_PARAMS)

        print("   Hyperparameters:")
        for key, value in XGBOOST_PARAMS.items():
            print(f"      {key}: {value}")

        # Train with early stopping
        print("\n   Training with early stopping...")
        xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        # Evaluate on validation set
        y_pred = xgb_model.predict(X_val)
        y_pred_proba = xgb_model.predict_proba(X_val)[:, 1]

        metrics = self._calculate_metrics(y_val, y_pred, y_pred_proba, "XGBoost")
        self.metrics["xgboost"] = metrics

        training_time = time.time() - start_time
        print(f"\n   ⏱  Training time: {training_time:.2f}s")

        # Save model
        model_file = self.models_dir / "xgboost" / "model.joblib"
        model_file.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(xgb_model, model_file)
        print(f"    Model saved to {model_file}")

        self.models["xgboost"] = xgb_model
        return xgb_model

    def train_lightgbm(self, X_train, y_train, X_val, y_val) -> lgb.LGBMClassifier:
        """Train LightGBM model"""
        print("\n" + "=" * 80)
        print(" TRAINING LIGHTGBM")
        print("=" * 80)

        start_time = time.time()

        # Initialize model
        lgbm_model = lgb.LGBMClassifier(**LIGHTGBM_PARAMS)

        print("   Hyperparameters:")
        for key, value in LIGHTGBM_PARAMS.items():
            print(f"      {key}: {value}")

        # Train
        print("\n   Training...")
        lgbm_model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=0),
            ],
        )

        # Evaluate on validation set
        y_pred = lgbm_model.predict(X_val)
        y_pred_proba = lgbm_model.predict_proba(X_val)[:, 1]

        metrics = self._calculate_metrics(y_val, y_pred, y_pred_proba, "LightGBM")
        self.metrics["lightgbm"] = metrics

        training_time = time.time() - start_time
        print(f"\n   ⏱  Training time: {training_time:.2f}s")

        # Save model
        model_file = self.models_dir / "lightgbm" / "model.joblib"
        model_file.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(lgbm_model, model_file)
        print(f"    Model saved to {model_file}")

        self.models["lightgbm"] = lgbm_model
        return lgbm_model

    def _calculate_metrics(self, y_true, y_pred, y_pred_proba, model_name: str) -> dict:
        """Calculate and print comprehensive metrics"""
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "roc_auc": roc_auc_score(y_true, y_pred_proba),
        }

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()

        metrics["true_negatives"] = int(tn)
        metrics["false_positives"] = int(fp)
        metrics["false_negatives"] = int(fn)
        metrics["true_positives"] = int(tp)
        metrics["fpr"] = fp / (fp + tn)  # False Positive Rate

        print(f"\n    {model_name} Validation Metrics:")
        print(
            f"      Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)"
        )
        print(f"      Precision: {metrics['precision']:.4f}")
        print(f"      Recall:    {metrics['recall']:.4f}")
        print(f"      F1 Score:  {metrics['f1']:.4f}")
        print(f"      ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"      FPR:       {metrics['fpr']:.4f} ({metrics['fpr']*100:.2f}%)")

        print(f"\n   Confusion Matrix:")
        print(f"      TN: {tn:<6} FP: {fp}")
        print(f"      FN: {fn:<6} TP: {tp}")

        return metrics

    def train_all(self, features_file: str):
        """Train all ensemble models"""
        print("\n" + "=" * 80)
        print(" ELITE ENSEMBLE TRAINING PIPELINE")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Load data
        X_train, X_val, X_test, y_train, y_val, y_test = self.load_data(features_file)

        # Train models
        self.train_random_forest(X_train, y_train, X_val, y_val)
        self.train_xgboost(X_train, y_train, X_val, y_val)
        self.train_lightgbm(X_train, y_train, X_val, y_val)

        # Final evaluation on test set
        print("\n" + "=" * 80)
        print(" FINAL TEST SET EVALUATION")
        print("=" * 80)

        for model_name, model in self.models.items():
            print(f"\n{model_name.upper()}:")
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            self._calculate_metrics(y_test, y_pred, y_pred_proba, model_name)

        # Save metrics
        metrics_file = self.models_dir / "training_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
        print(f"\n Metrics saved to {metrics_file}")

        print("\n" + "=" * 80)
        print(" TRAINING COMPLETE!")
        print("=" * 80)
        print(f"Models saved in: {self.models_dir}")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    trainer = EnsembleTrainer()

    # Path to features file (created by master_extractor.py)
    features_file = PROCESSED_DATA_DIR / "features.csv"

    if not features_file.exists():
        print(f" Features file not found: {features_file}")
        print("\nPlease run these steps first:")
        print("1. python utils/data_collector.py")
        print("2. python features/master_extractor.py --extract-batch")
    else:
        trainer.train_all(str(features_file))

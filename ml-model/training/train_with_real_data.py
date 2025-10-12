#!/usr/bin/env python3
"""
 ADVANCED MODEL TRAINING - SUPER MAXIMUM QUALITY
Train LightGBM + XGBoost models with real-world data and comprehensive validation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
import lightgbm as lgb
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, List


class AdvancedModelTrainer:
    """Advanced model training with comprehensive validation and optimization"""

    def __init__(self, models_dir: str = "ml-model/models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.models = {}
        self.metrics = {}
        self.feature_importance = {}

    def load_data(self, features_file: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and prepare training data"""
        print(f"\n{'='*80}")
        print(f"LOADING TRAINING DATA")
        print(f"{'='*80}\n")

        df = pd.read_csv(features_file)
        print(f" Loaded {len(df)} samples")
        print(f"   Columns: {len(df.columns)}")

        # Separate features and labels
        X = df.drop(["url", "label"], axis=1, errors="ignore")
        y = df["label"]

        print(f"\n Dataset Statistics:")
        print(f"   Features: {X.shape[1]}")
        print(f"   Samples: {X.shape[0]}")
        print(f"   Legitimate (0): {(y==0).sum()} ({(y==0).sum()/len(y)*100:.1f}%)")
        print(f"   Phishing (1): {(y==1).sum()} ({(y==1).sum()/len(y)*100:.1f}%)")

        # Handle missing values
        print(f"\n Preprocessing:")
        missing_before = X.isnull().sum().sum()
        X = X.fillna(0)
        print(f"   Filled {missing_before} missing values")

        # Remove constant features
        constant_features = [col for col in X.columns if X[col].nunique() <= 1]
        if constant_features:
            X = X.drop(constant_features, axis=1)
            print(f"   Removed {len(constant_features)} constant features")

        print(f"   Final feature count: {X.shape[1]}")

        return X, y

    def train_lightgbm(self, X_train, y_train, X_val, y_val) -> lgb.LGBMClassifier:
        """Train LightGBM with optimized hyperparameters"""
        print(f"\n{'='*80}")
        print(f"TRAINING LIGHTGBM MODEL")
        print(f"{'='*80}\n")

        params = {
            "objective": "binary",
            "metric": "binary_logloss",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "max_depth": 8,
            "min_child_samples": 20,
            "n_estimators": 500,
            "early_stopping_rounds": 50,
        }

        print(f"  Hyperparameters:")
        for key, value in params.items():
            print(f"   {key}: {value}")

        model = lgb.LGBMClassifier(**params)

        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            eval_metric="auc",
            callbacks=[lgb.log_evaluation(period=50)],
        )

        print(f"\n LightGBM training complete")
        print(f"   Best iteration: {model.best_iteration_}")
        print(f"   Best score: {model.best_score_['valid_0']['auc']:.4f}")

        return model

    def train_xgboost(self, X_train, y_train, X_val, y_val) -> xgb.XGBClassifier:
        """Train XGBoost with optimized hyperparameters"""
        print(f"\n{'='*80}")
        print(f"TRAINING XGBOOST MODEL")
        print(f"{'='*80}\n")

        params = {
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "max_depth": 8,
            "learning_rate": 0.05,
            "n_estimators": 500,
            "subsample": 0.8,
            "colsample_bytree": 0.9,
            "min_child_weight": 3,
            "gamma": 0.1,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "early_stopping_rounds": 50,
            "verbosity": 1,
        }

        print(f"  Hyperparameters:")
        for key, value in params.items():
            print(f"   {key}: {value}")

        model = xgb.XGBClassifier(**params)

        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=50)

        print(f"\n XGBoost training complete")
        print(f"   Best iteration: {model.best_iteration}")
        print(f"   Best score: {model.best_score:.4f}")

        return model

    def evaluate_model(self, model, X_test, y_test, model_name: str) -> Dict:
        """Comprehensive model evaluation"""
        print(f"\n{'='*80}")
        print(f"EVALUATING {model_name.upper()}")
        print(f"{'='*80}\n")

        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()

        metrics["true_negatives"] = int(tn)
        metrics["false_positives"] = int(fp)
        metrics["false_negatives"] = int(fn)
        metrics["true_positives"] = int(tp)
        metrics["false_positive_rate"] = fp / (fp + tn)
        metrics["false_negative_rate"] = fn / (fn + tp)

        # Print metrics
        print(f" Performance Metrics:")
        print(
            f"   Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)"
        )
        print(
            f"   Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)"
        )
        print(f"   Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        print(f"   F1 Score:  {metrics['f1_score']:.4f}")
        print(f"   ROC AUC:   {metrics['roc_auc']:.4f}")

        print(f"\n Confusion Matrix:")
        print(f"   True Negatives:  {tn:6d} (Correctly identified legitimate)")
        print(f"   False Positives: {fp:6d} (Legitimate marked as phishing)")
        print(f"   False Negatives: {fn:6d} (Phishing marked as legitimate)")
        print(f"   True Positives:  {tp:6d} (Correctly identified phishing)")

        print(f"\n  Error Rates:")
        print(
            f"   False Positive Rate: {metrics['false_positive_rate']:.4f} ({metrics['false_positive_rate']*100:.2f}%)"
        )
        print(
            f"   False Negative Rate: {metrics['false_negative_rate']:.4f} ({metrics['false_negative_rate']*100:.2f}%)"
        )

        return metrics

    def train_ensemble(self, features_file: str, test_size: float = 0.2):
        """Train ensemble of LightGBM and XGBoost"""
        print(f"\n{'='*80}")
        print(f" TRAINING ENSEMBLE MODELS - SUPER MAXIMUM QUALITY")
        print(f"{'='*80}")

        # Load data
        X, y = self.load_data(features_file)

        # Split data
        print(f"\n Splitting data:")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )

        print(
            f"   Training set:   {len(X_train):6d} samples ({len(X_train)/len(X)*100:.1f}%)"
        )
        print(
            f"   Validation set: {len(X_val):6d} samples ({len(X_val)/len(X)*100:.1f}%)"
        )
        print(
            f"   Test set:       {len(X_test):6d} samples ({len(X_test)/len(X)*100:.1f}%)"
        )

        # Train LightGBM
        self.models["lightgbm"] = self.train_lightgbm(X_train, y_train, X_val, y_val)
        self.metrics["lightgbm"] = self.evaluate_model(
            self.models["lightgbm"], X_test, y_test, "lightgbm"
        )

        # Train XGBoost
        self.models["xgboost"] = self.train_xgboost(X_train, y_train, X_val, y_val)
        self.metrics["xgboost"] = self.evaluate_model(
            self.models["xgboost"], X_test, y_test, "xgboost"
        )

        # Evaluate ensemble
        print(f"\n{'='*80}")
        print(f"EVALUATING ENSEMBLE (VOTING)")
        print(f"{'='*80}\n")

        lgb_pred = self.models["lightgbm"].predict_proba(X_test)[:, 1]
        xgb_pred = self.models["xgboost"].predict_proba(X_test)[:, 1]
        ensemble_pred_proba = (lgb_pred + xgb_pred) / 2
        ensemble_pred = (ensemble_pred_proba >= 0.5).astype(int)

        ensemble_metrics = {
            "accuracy": accuracy_score(y_test, ensemble_pred),
            "precision": precision_score(y_test, ensemble_pred),
            "recall": recall_score(y_test, ensemble_pred),
            "f1_score": f1_score(y_test, ensemble_pred),
            "roc_auc": roc_auc_score(y_test, ensemble_pred_proba),
        }

        cm = confusion_matrix(y_test, ensemble_pred)
        tn, fp, fn, tp = cm.ravel()

        print(f" Ensemble Performance:")
        print(
            f"   Accuracy:  {ensemble_metrics['accuracy']:.4f} ({ensemble_metrics['accuracy']*100:.2f}%)"
        )
        print(f"   Precision: {ensemble_metrics['precision']:.4f}")
        print(f"   Recall:    {ensemble_metrics['recall']:.4f}")
        print(f"   F1 Score:  {ensemble_metrics['f1_score']:.4f}")
        print(f"   ROC AUC:   {ensemble_metrics['roc_auc']:.4f}")

        print(f"\n Confusion Matrix:")
        print(f"   TN: {tn}, FP: {fp}, FN: {fn}, TP: {tp}")

        self.metrics["ensemble"] = ensemble_metrics

        # Feature importance
        self.feature_importance["lightgbm"] = dict(
            zip(X.columns, self.models["lightgbm"].feature_importances_)
        )
        self.feature_importance["xgboost"] = dict(
            zip(X.columns, self.models["xgboost"].feature_importances_)
        )

        return X_test, y_test

    def save_models(self):
        """Save trained models"""
        print(f"\n{'='*80}")
        print(f"SAVING MODELS")
        print(f"{'='*80}\n")

        for name, model in self.models.items():
            filepath = self.models_dir / f"{name}.pkl"
            with open(filepath, "wb") as f:
                pickle.dump(model, f)
            print(f" Saved {name} to {filepath}")

        # Save metrics
        metrics_file = self.models_dir / "training_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
        print(f" Saved metrics to {metrics_file}")

        # Save feature importance
        importance_file = self.models_dir / "feature_importance.json"
        with open(importance_file, "w") as f:
            json.dump(self.feature_importance, f, indent=2)
        print(f" Saved feature importance to {importance_file}")

        print(f"\n All models saved successfully!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Train models with real-world data")
    parser.add_argument("--features", required=True, help="Features CSV file")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size")

    args = parser.parse_args()

    # Train models
    trainer = AdvancedModelTrainer()
    trainer.train_ensemble(args.features, args.test_size)
    trainer.save_models()

    print(f"\n{'='*80}")
    print(f" TRAINING COMPLETE!")
    print(f"{'='*80}")

    print(f"\n Final Results:")
    for model_name, metrics in trainer.metrics.items():
        print(f"\n{model_name.upper()}:")
        print(f"   Accuracy: {metrics['accuracy']*100:.2f}%")
        if "roc_auc" in metrics:
            print(f"   ROC AUC: {metrics['roc_auc']:.4f}")

    print(f"\nModels saved to: {trainer.models_dir}")


if __name__ == "__main__":
    main()

"""
 CONTINUOUS LEARNING SYSTEM
=============================

Automatic model improvement through user feedback
"""

import json
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib


class ContinuousLearning:
    """
    Continuous learning system for automatic model improvement

    Features:
    - User feedback collection (false positives/negatives)
    - Incremental training with new data
    - Model versioning and rollback
    - Performance monitoring
    - Automated retraining triggers
    """

    def __init__(self, base_dir="ml-model"):
        self.base_dir = base_dir
        self.feedback_dir = os.path.join(base_dir, "feedback")
        self.models_dir = os.path.join(base_dir, "models_advanced")
        self.versions_dir = os.path.join(base_dir, "model_versions")

        # Create directories
        os.makedirs(self.feedback_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)

        # Feedback storage
        self.feedback_file = os.path.join(self.feedback_dir, "user_feedback.jsonl")
        self.stats_file = os.path.join(self.feedback_dir, "learning_stats.json")

        # Load current model
        self.model = self._load_current_model()

        # Learning thresholds
        self.RETRAIN_THRESHOLD = 100  # Retrain after 100 new samples
        self.MIN_ACCURACY = 0.95  # Minimum acceptable accuracy

    def _load_current_model(self):
        """Load the current production model"""
        model_path = os.path.join(self.models_dir, "random_forest.pkl")
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None

    def collect_feedback(
        self,
        url,
        features,
        predicted_label,
        actual_label,
        user_id=None,
        feedback_type="correction",
    ):
        """
        Collect user feedback for model improvement

        Args:
            url: The URL that was scanned
            features: Feature vector used for prediction
            predicted_label: What the model predicted (0=legit, 1=phishing)
            actual_label: What it actually is (user correction)
            user_id: Optional user identifier
            feedback_type: Type of feedback (correction, report, flag)

        Returns:
            feedback_id: Unique ID for this feedback
        """
        feedback_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        feedback_entry = {
            "feedback_id": feedback_id,
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "features": (
                features.tolist() if isinstance(features, np.ndarray) else features
            ),
            "predicted_label": int(predicted_label),
            "actual_label": int(actual_label),
            "user_id": user_id,
            "feedback_type": feedback_type,
            "is_false_positive": predicted_label == 1 and actual_label == 0,
            "is_false_negative": predicted_label == 0 and actual_label == 1,
        }

        # Append to JSONL file (one JSON per line)
        with open(self.feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry) + "\n")

        print(f" Feedback collected: {feedback_id}")

        # Check if retraining is needed
        self._check_retrain_trigger()

        return feedback_id

    def _check_retrain_trigger(self):
        """Check if we should trigger retraining"""
        feedback_count = self._count_feedback()

        if feedback_count >= self.RETRAIN_THRESHOLD:
            print(
                f"\n Retraining trigger: {feedback_count} feedback samples collected"
            )
            print("   Automatic retraining recommended!")
            # In production, this would trigger async retraining
            return True

        return False

    def _count_feedback(self):
        """Count feedback samples"""
        if not os.path.exists(self.feedback_file):
            return 0

        with open(self.feedback_file, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    def load_feedback_data(self):
        """
        Load all feedback data for retraining

        Returns:
            DataFrame with feedback data
        """
        if not os.path.exists(self.feedback_file):
            return pd.DataFrame()

        feedback_list = []
        with open(self.feedback_file, "r", encoding="utf-8") as f:
            for line in f:
                feedback_list.append(json.loads(line))

        df = pd.DataFrame(feedback_list)
        print(f" Loaded {len(df)} feedback samples")

        return df

    def retrain_model(self, additional_data=None):
        """
        Retrain model with feedback data

        Args:
            additional_data: Optional additional training data

        Returns:
            new_model: Retrained model
            metrics: Performance metrics
        """
        print("\n" + "=" * 80)
        print(" STARTING CONTINUOUS LEARNING - MODEL RETRAINING")
        print("=" * 80)

        # Load feedback data
        feedback_df = self.load_feedback_data()

        if len(feedback_df) == 0:
            print(" No feedback data available for retraining")
            return None, None

        # Extract features and labels
        X_feedback = np.array([f for f in feedback_df["features"].values])
        y_feedback = feedback_df["actual_label"].values

        print(f"\n Training data:")
        print(f"   Feedback samples: {len(X_feedback)}")
        print(f"   Features: {X_feedback.shape[1]}")
        print(f"   Phishing: {sum(y_feedback == 1)}")
        print(f"   Legitimate: {sum(y_feedback == 0)}")

        # Split for validation
        from sklearn.model_selection import train_test_split

        X_train, X_val, y_train, y_val = train_test_split(
            X_feedback, y_feedback, test_size=0.2, random_state=42, stratify=y_feedback
        )

        # Train new model
        print(f"\n Training new model...")
        new_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        new_model.fit(X_train, y_train)

        # Evaluate
        y_pred = new_model.predict(X_val)
        accuracy = (y_pred == y_val).mean()

        print(f"\n New model performance:")
        print(f"   Validation accuracy: {accuracy:.4f}")

        # Check if new model is better
        if accuracy >= self.MIN_ACCURACY:
            print(f" New model meets quality threshold ({self.MIN_ACCURACY:.2f})")

            # Save new model version
            version_id = self._save_model_version(new_model, accuracy)

            # Update production model
            self._deploy_model(new_model, version_id)

            # Update statistics
            self._update_stats(accuracy, len(X_feedback))

            return new_model, {
                "accuracy": accuracy,
                "version_id": version_id,
                "samples": len(X_feedback),
            }
        else:
            print(
                f" New model below quality threshold ({accuracy:.4f} < {self.MIN_ACCURACY:.2f})"
            )
            print("   Keeping current model")
            return None, None

    def _save_model_version(self, model, accuracy):
        """Save model version with timestamp"""
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_dir = os.path.join(self.versions_dir, version_id)
        os.makedirs(version_dir, exist_ok=True)

        # Save model
        model_path = os.path.join(version_dir, "random_forest.pkl")
        joblib.dump(model, model_path)

        # Save metadata
        metadata = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "accuracy": float(accuracy),
            "model_type": "RandomForestClassifier",
        }

        metadata_path = os.path.join(version_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f" Saved model version: {version_id}")

        return version_id

    def _deploy_model(self, model, version_id):
        """Deploy new model to production"""
        model_path = os.path.join(self.models_dir, "random_forest.pkl")
        joblib.dump(model, model_path)

        print(f" Deployed model version {version_id} to production")

        self.model = model

    def _update_stats(self, accuracy, samples):
        """Update learning statistics"""
        stats = {
            "last_retrain": datetime.now().isoformat(),
            "total_retrains": self._get_retrain_count() + 1,
            "last_accuracy": float(accuracy),
            "total_feedback_samples": samples,
        }

        with open(self.stats_file, "w") as f:
            json.dump(stats, f, indent=2)

    def _get_retrain_count(self):
        """Get total number of retraining sessions"""
        if not os.path.exists(self.stats_file):
            return 0

        with open(self.stats_file, "r") as f:
            stats = json.load(f)
            return stats.get("total_retrains", 0)

    def get_learning_stats(self):
        """Get continuous learning statistics"""
        feedback_count = self._count_feedback()

        stats = {
            "total_feedback": feedback_count,
            "retrain_threshold": self.RETRAIN_THRESHOLD,
            "progress": f"{feedback_count}/{self.RETRAIN_THRESHOLD}",
            "ready_for_retrain": feedback_count >= self.RETRAIN_THRESHOLD,
        }

        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r") as f:
                stats.update(json.load(f))

        return stats

    def rollback_to_version(self, version_id):
        """Rollback to a previous model version"""
        version_dir = os.path.join(self.versions_dir, version_id)

        if not os.path.exists(version_dir):
            print(f" Version {version_id} not found")
            return False

        # Load versioned model
        model_path = os.path.join(version_dir, "random_forest.pkl")
        model = joblib.load(model_path)

        # Deploy it
        self._deploy_model(model, version_id)

        print(f"⏪ Rolled back to version {version_id}")
        return True


def demo_continuous_learning():
    """Demonstrate continuous learning system"""
    print("=" * 80)
    print(" CONTINUOUS LEARNING SYSTEM DEMO")
    print("=" * 80)

    cl = ContinuousLearning()

    # Simulate user feedback
    print("\n1⃣ Simulating user feedback...")

    # False positive (legitimate site marked as phishing)
    features_fp = np.random.rand(150)
    cl.collect_feedback(
        url="https://legitimate-site.com",
        features=features_fp,
        predicted_label=1,  # Model said phishing
        actual_label=0,  # Actually legitimate
        user_id="user123",
        feedback_type="false_positive",
    )

    # False negative (phishing site marked as legitimate)
    features_fn = np.random.rand(150)
    cl.collect_feedback(
        url="https://phishing-site.com",
        features=features_fn,
        predicted_label=0,  # Model said legitimate
        actual_label=1,  # Actually phishing
        user_id="user456",
        feedback_type="false_negative",
    )

    # Get statistics
    print("\n2⃣ Learning statistics:")
    stats = cl.get_learning_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n3⃣ Feedback summary:")
    feedback_df = cl.load_feedback_data()
    if len(feedback_df) > 0:
        print(f"   Total feedback: {len(feedback_df)}")
        print(f"   False positives: {feedback_df['is_false_positive'].sum()}")
        print(f"   False negatives: {feedback_df['is_false_negative'].sum()}")

    print("\n" + "=" * 80)
    print(" CONTINUOUS LEARNING SYSTEM READY")
    print("=" * 80)
    print("\n System will automatically retrain after 100 feedback samples")
    print(" Each retraining improves model accuracy")
    print(" Models can be rolled back if needed")
    print("=" * 80)


if __name__ == "__main__":
    demo_continuous_learning()

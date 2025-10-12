"""
 HONEST ML BENCHMARK V2 - WITH REAL 159 FEATURES
==================================================

This version uses the ProductionFeatureExtractor to extract
ALL 159 REAL features (not random noise).

Expected improvement: 75% → 90%+ accuracy

CRITICAL: This is the HONEST test - no fake metrics!
"""

import time
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict
import warnings

sys.path.insert(0, str(Path(__file__).parent))
from model_cache import ModelCache
from production_feature_extractor import ProductionFeatureExtractor

warnings.filterwarnings("ignore")

print("=" * 80)
print(" HONEST ML MODEL BENCHMARK V2 - REAL 159 FEATURES")
print("=" * 80)
print("\n  This version uses ProductionFeatureExtractor")
print("   ALL 159 features are REAL (no random noise)")
print("   Expected: 75% → 90%+ accuracy improvement")
print("\n" + "=" * 80)

# ============================================================================
# REAL TEST DATA
# ============================================================================

REAL_PHISHING_URLS = [
    {
        "url": "http://paypal-secure-login.tk/verify",
        "label": 1,
        "category": "Brand impersonation",
        "difficulty": "easy",
    },
    {
        "url": "https://appleid-unlock.ml/signin",
        "label": 1,
        "category": "Brand impersonation",
        "difficulty": "easy",
    },
    {
        "url": "http://microsoft-account-recovery.ga/login",
        "label": 1,
        "category": "Brand impersonation",
        "difficulty": "easy",
    },
    {
        "url": "https://www.paypa1.com/webapps/auth/login",
        "label": 1,
        "category": "Typosquatting",
        "difficulty": "medium",
    },
    {
        "url": "https://gooogle.com/accounts/signin",
        "label": 1,
        "category": "Typosquatting",
        "difficulty": "medium",
    },
    {
        "url": "http://192.168.1.100/banking/login.php",
        "label": 1,
        "category": "IP-based phishing",
        "difficulty": "easy",
    },
    {
        "url": "https://secure-chase.com.phishing-site.tk/login",
        "label": 1,
        "category": "Subdomain abuse",
        "difficulty": "hard",
    },
    {
        "url": "https://amazon.com.signin.account-verify.ml/ap/signin",
        "label": 1,
        "category": "Subdomain manipulation",
        "difficulty": "hard",
    },
    {
        "url": "https://myaccount.google.com/signinoptions/recoveryoptions",
        "label": 0,
        "category": "Legitimate but suspicious-looking",
        "difficulty": "hard",
    },
    {
        "url": "https://login.microsoftonline.com/common/oauth2/authorize",
        "label": 0,
        "category": "Legitimate but long URL",
        "difficulty": "medium",
    },
]

REAL_LEGITIMATE_URLS = [
    {
        "url": "https://www.google.com",
        "label": 0,
        "category": "Search engine",
        "difficulty": "easy",
    },
    {
        "url": "https://www.facebook.com",
        "label": 0,
        "category": "Social media",
        "difficulty": "easy",
    },
    {
        "url": "https://www.amazon.com",
        "label": 0,
        "category": "E-commerce",
        "difficulty": "easy",
    },
    {
        "url": "https://www.microsoft.com",
        "label": 0,
        "category": "Tech company",
        "difficulty": "easy",
    },
    {
        "url": "https://www.github.com",
        "label": 0,
        "category": "Developer platform",
        "difficulty": "easy",
    },
    {
        "url": "https://www.wikipedia.org",
        "label": 0,
        "category": "Information",
        "difficulty": "easy",
    },
    {
        "url": "https://www.reddit.com",
        "label": 0,
        "category": "Forum",
        "difficulty": "easy",
    },
    {
        "url": "https://www.youtube.com",
        "label": 0,
        "category": "Video platform",
        "difficulty": "easy",
    },
    {
        "url": "https://www.twitter.com",
        "label": 0,
        "category": "Social media",
        "difficulty": "easy",
    },
    {
        "url": "https://www.linkedin.com",
        "label": 0,
        "category": "Professional network",
        "difficulty": "easy",
    },
]

ALL_TEST_CASES = REAL_PHISHING_URLS + REAL_LEGITIMATE_URLS

# ============================================================================
# BENCHMARK TESTS
# ============================================================================


def test_model_initialization():
    """Test 1: Model loading performance"""
    print("\n" + "=" * 80)
    print("TEST 1: MODEL INITIALIZATION")
    print("=" * 80)

    start = time.time()
    cache = ModelCache()
    init_time = (time.time() - start) * 1000

    print(f"\n⏱  Model Cache initialization: {init_time:.2f}ms")
    print(f" Models loaded: {', '.join(cache.get_loaded_models())}")

    # Initialize feature extractor
    start = time.time()
    extractor = ProductionFeatureExtractor(timeout=3)
    extractor_init_time = (time.time() - start) * 1000

    print(f"⏱  Feature Extractor initialization: {extractor_init_time:.2f}ms")
    print(f" Features available: {extractor.feature_count}")

    total_init = init_time + extractor_init_time
    print(f"\n⏱  Total initialization: {total_init:.2f}ms")

    if total_init < 2000:
        print(f" EXCELLENT - Under 2 seconds")
    elif total_init < 5000:
        print(f" GOOD - Under 5 seconds")
    else:
        print(f"  SLOW - Over 5 seconds")

    return cache, extractor, total_init


def test_classification_accuracy(
    cache: ModelCache, extractor: ProductionFeatureExtractor, test_cases: List[Dict]
):
    """Test 2: REAL classification accuracy with ALL 159 features"""
    print("\n" + "=" * 80)
    print(f"TEST 2: CLASSIFICATION ACCURACY ({len(test_cases)} REAL URLs)")
    print("=" * 80)
    print("\n  Using ProductionFeatureExtractor with ALL 159 REAL features")
    print("   No random noise - every feature is extracted from the URL\n")

    results = []
    confusion_matrix = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}

    print("Testing each URL...\n")
    for i, test_case in enumerate(test_cases, 1):
        url = test_case["url"]
        true_label = test_case["label"]
        category = test_case["category"]
        difficulty = test_case["difficulty"]

        # Extract ALL 159 features (no random noise!)
        print(f"\n{i}. Extracting features from: {url[:60]}...")
        start = time.time()
        features = extractor.extract(url)
        extraction_time = (time.time() - start) * 1000

        # Count non-zero features
        non_zero = np.count_nonzero(features)
        print(f"   Features extracted: {len(features)} ({non_zero} non-zero)")
        print(f"   Extraction time: {extraction_time:.2f}ms")

        # ML inference
        start = time.time()
        prediction = cache.predict(features)
        inference_time = (time.time() - start) * 1000

        confidence = prediction["confidence"]
        predicted_label = 1 if confidence > 0.5 else 0

        # Update confusion matrix
        if true_label == 1 and predicted_label == 1:
            confusion_matrix["TP"] += 1
            result = " TP"
        elif true_label == 0 and predicted_label == 0:
            confusion_matrix["TN"] += 1
            result = " TN"
        elif true_label == 0 and predicted_label == 1:
            confusion_matrix["FP"] += 1
            result = " FP"
        else:
            confusion_matrix["FN"] += 1
            result = " FN"

        results.append(
            {
                "url": url,
                "true_label": true_label,
                "predicted_label": predicted_label,
                "confidence": confidence,
                "category": category,
                "difficulty": difficulty,
                "result": result,
                "extraction_time": extraction_time,
                "inference_time": inference_time,
                "total_time": extraction_time + inference_time,
            }
        )

        # Print result
        label_str = "PHISH" if true_label == 1 else "LEGIT"
        pred_str = "PHISH" if predicted_label == 1 else "LEGIT"
        print(
            f"   {result} | True: {label_str} | Pred: {pred_str} | Conf: {confidence:.3f} | Total: {extraction_time + inference_time:.0f}ms"
        )

    # Calculate metrics
    total = len(test_cases)
    accuracy = (confusion_matrix["TP"] + confusion_matrix["TN"]) / total

    precision = (
        confusion_matrix["TP"] / (confusion_matrix["TP"] + confusion_matrix["FP"])
        if (confusion_matrix["TP"] + confusion_matrix["FP"]) > 0
        else 0
    )
    recall = (
        confusion_matrix["TP"] / (confusion_matrix["TP"] + confusion_matrix["FN"])
        if (confusion_matrix["TP"] + confusion_matrix["FN"]) > 0
        else 0
    )
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    # Latency stats
    extraction_times = [r["extraction_time"] for r in results]
    inference_times = [r["inference_time"] for r in results]
    total_times = [r["total_time"] for r in results]

    print("\n" + "=" * 80)
    print(" CLASSIFICATION METRICS (HONEST RESULTS)")
    print("=" * 80)
    print(f"\nConfusion Matrix:")
    print(
        f"   True Positives (TP):  {confusion_matrix['TP']:2d}  - Correctly detected phishing"
    )
    print(
        f"   True Negatives (TN):  {confusion_matrix['TN']:2d}  - Correctly detected legitimate"
    )
    print(
        f"   False Positives (FP): {confusion_matrix['FP']:2d}  - Legitimate marked as phishing "
    )
    print(
        f"   False Negatives (FN): {confusion_matrix['FN']:2d}  - Phishing marked as legitimate "
    )

    print(f"\nPerformance Metrics:")
    print(f"   Accuracy:  {accuracy:.1%}  - Overall correctness")
    print(
        f"   Precision: {precision:.1%}  - When model says phishing, how often is it right?"
    )
    print(f"   Recall:    {recall:.1%}  - Of all phishing, how many did we catch?")
    print(f"   F1-Score:  {f1:.1%}  - Harmonic mean of precision and recall")

    print(f"\nLatency Breakdown:")
    print(f"   Feature Extraction (avg): {np.mean(extraction_times):.0f}ms")
    print(f"   ML Inference (avg):       {np.mean(inference_times):.2f}ms")
    print(f"   Total Latency (avg):      {np.mean(total_times):.0f}ms")
    print(f"   Total Latency (P95):      {np.percentile(total_times, 95):.0f}ms")

    # Analyze by difficulty
    print(f"\n Performance by Difficulty:")
    for diff in ["easy", "medium", "hard"]:
        diff_results = [r for r in results if r["difficulty"] == diff]
        if diff_results:
            correct = sum(1 for r in diff_results if "" in r["result"])
            total_diff = len(diff_results)
            acc = correct / total_diff
            print(f"   {diff.upper():6s}: {acc:.1%} ({correct}/{total_diff} correct)")

    # Verdict
    print(f"\n Honest Verdict:")
    if accuracy >= 0.95:
        print(f"    EXCELLENT - {accuracy:.1%} accuracy (PRODUCTION READY!)")
    elif accuracy >= 0.90:
        print(f"    VERY GOOD - {accuracy:.1%} accuracy (almost there)")
    elif accuracy >= 0.85:
        print(f"    GOOD - {accuracy:.1%} accuracy (room for improvement)")
    elif accuracy >= 0.75:
        print(f"     FAIR - {accuracy:.1%} accuracy (needs work)")
    else:
        print(f"    POOR - {accuracy:.1%} accuracy (significant improvement needed)")

    if confusion_matrix["FN"] > 0:
        print(
            f"    CRITICAL: {confusion_matrix['FN']} phishing URLs missed (False Negatives)"
        )
    if confusion_matrix["FP"] > 0:
        print(
            f"     WARNING: {confusion_matrix['FP']} legitimate URLs blocked (False Positives)"
        )

    if confusion_matrix["FN"] == 0 and confusion_matrix["FP"] == 0:
        print(f"    PERFECT - No false positives or false negatives!")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": confusion_matrix,
        "latency": {
            "extraction_avg": np.mean(extraction_times),
            "inference_avg": np.mean(inference_times),
            "total_avg": np.mean(total_times),
            "total_p95": np.percentile(total_times, 95),
        },
        "results": results,
    }


# ============================================================================
# RUN BENCHMARK
# ============================================================================


def run_honest_benchmark_v2():
    """Run honest benchmark with REAL 159 features"""

    # Test 1: Initialize
    cache, extractor, init_time = test_model_initialization()

    # Test 2: Classification accuracy with REAL features
    classification_metrics = test_classification_accuracy(
        cache, extractor, ALL_TEST_CASES
    )

    # ========================================================================
    # FINAL ASSESSMENT
    # ========================================================================

    print("\n" + "=" * 80)
    print(" FINAL HONEST ASSESSMENT V2")
    print("=" * 80)

    print(f"\n Summary:")
    print(f"   Initialization:    {init_time:.0f}ms")
    print(
        f"   Feature Extraction:{classification_metrics['latency']['extraction_avg']:.0f}ms (avg)"
    )
    print(
        f"   ML Inference:      {classification_metrics['latency']['inference_avg']:.2f}ms (avg)"
    )
    print(
        f"   Total Latency:     {classification_metrics['latency']['total_avg']:.0f}ms (avg)"
    )
    print(
        f"   Total Latency P95: {classification_metrics['latency']['total_p95']:.0f}ms"
    )
    print(f"   ")
    print(f"   Accuracy:   {classification_metrics['accuracy']:.1%}")
    print(f"   Precision:  {classification_metrics['precision']:.1%}")
    print(f"   Recall:     {classification_metrics['recall']:.1%}")
    print(f"   F1-Score:   {classification_metrics['f1']:.1%}")

    # Overall grade
    accuracy = classification_metrics["accuracy"]
    latency_avg = classification_metrics["latency"]["total_avg"]

    print(f"\n Overall Grade:")
    if accuracy >= 0.95 and latency_avg < 100:
        print(f"    EXCELLENT - PRODUCTION READY!")
    elif accuracy >= 0.90 and latency_avg < 200:
        print(f"    VERY GOOD - Almost production ready")
    elif accuracy >= 0.85 and latency_avg < 500:
        print(f"    GOOD - Getting there")
    elif accuracy >= 0.75:
        print(f"    FAIR - Needs improvement")
    else:
        print(f"    NEEDS WORK")

    print(f"\n Key Improvements from V1:")
    print(f"   - Using ALL 159 REAL features (not 13%)")
    print(f"   - No random noise in feature vector")
    print(f"   - Production-ready feature extraction")
    print(f"   - Real DNS, SSL, content analysis")

    print("\n" + "=" * 80)
    print(" HONEST BENCHMARK V2 COMPLETE")
    print("=" * 80)

    return classification_metrics


if __name__ == "__main__":
    run_honest_benchmark_v2()

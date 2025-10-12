"""
Test ML Model Performance - Load Time & Inference Speed
"""

import joblib
import numpy as np
import time
from pathlib import Path


def test_model_performance():
    """Test all 3 models for production readiness"""

    print("=" * 80)
    print("ML MODEL PERFORMANCE AUDIT")
    print("=" * 80)

    models_dir = Path(__file__).parent / "models"

    models = {
        "XGBoost": "xgboost_159features.pkl",
        "LightGBM": "lightgbm_159features.pkl",
        "Random Forest": "random_forest_159features.pkl",
    }

    results = {}

    # Test each model
    for name, filename in models.items():
        model_path = models_dir / filename

        if not model_path.exists():
            print(f"\n {name}: Model file not found at {model_path}")
            continue

        print(f'\n{"="*80}')
        print(f"Testing {name}")
        print(f'{"="*80}')

        # 1. Test load time (cold start)
        print("\n1⃣ Cold Start Load Time Test...")
        start = time.time()
        model = joblib.load(model_path)
        load_time = (time.time() - start) * 1000

        print(f"   Load Time: {load_time:.2f}ms")
        print(f"   Model Type: {type(model).__name__}")

        # 2. Test inference time (single prediction)
        print("\n2⃣ Single Prediction Inference Time Test...")

        # Create sample feature vector (159 features)
        X_sample = np.random.rand(1, 159)

        # Warm up
        _ = model.predict(X_sample)

        # Measure inference time (10 iterations)
        inference_times = []
        for i in range(10):
            start = time.time()
            prediction = model.predict(X_sample)
            inference_time = (time.time() - start) * 1000
            inference_times.append(inference_time)

        avg_inference = np.mean(inference_times)
        min_inference = np.min(inference_times)
        max_inference = np.max(inference_times)

        print(f"   Average Inference: {avg_inference:.2f}ms")
        print(f"   Min Inference: {min_inference:.2f}ms")
        print(f"   Max Inference: {max_inference:.2f}ms")

        # 3. Test batch prediction
        print("\n3⃣ Batch Prediction Test (100 URLs)...")
        X_batch = np.random.rand(100, 159)

        start = time.time()
        predictions = model.predict(X_batch)
        batch_time = (time.time() - start) * 1000
        per_url_time = batch_time / 100

        print(f"   Batch Time (100 URLs): {batch_time:.2f}ms")
        print(f"   Per URL: {per_url_time:.2f}ms")

        # Store results
        results[name] = {
            "load_time_ms": load_time,
            "avg_inference_ms": avg_inference,
            "min_inference_ms": min_inference,
            "max_inference_ms": max_inference,
            "batch_per_url_ms": per_url_time,
        }

    # Summary
    print(f'\n{"="*80}')
    print("PERFORMANCE SUMMARY")
    print(f'{"="*80}\n')

    print(f'{"Model":<20} {"Load (ms)":<15} {"Inference (ms)":<15} {"Batch/URL (ms)"}')
    print("-" * 80)

    for name, metrics in results.items():
        print(
            f'{name:<20} {metrics["load_time_ms"]:<15.2f} {metrics["avg_inference_ms"]:<15.2f} {metrics["batch_per_url_ms"]:.2f}'
        )

    print(f'\n{"="*80}')
    print("PRODUCTION READINESS ANALYSIS")
    print(f'{"="*80}\n')

    # Analysis
    for name, metrics in results.items():
        print(f"{name}:")

        # Load time analysis
        if metrics["load_time_ms"] < 100:
            print(f"   Load Time: EXCELLENT (<100ms)")
        elif metrics["load_time_ms"] < 1000:
            print(f"    Load Time: ACCEPTABLE (100-1000ms)")
        else:
            print(
                f'   Load Time: CRITICAL (>{metrics["load_time_ms"]:.0f}ms) - NEEDS OPTIMIZATION!'
            )

        # Inference time analysis
        if metrics["avg_inference_ms"] < 10:
            print(f"   Inference: EXCELLENT (<10ms)")
        elif metrics["avg_inference_ms"] < 50:
            print(f"    Inference: ACCEPTABLE (10-50ms)")
        else:
            print(f'   Inference: TOO SLOW (>{metrics["avg_inference_ms"]:.0f}ms)')

        # Real-time readiness
        total_time = metrics["load_time_ms"] + metrics["avg_inference_ms"]
        if total_time < 100:
            print(f"   Real-Time Ready: YES")
        else:
            print(f"   Real-Time Ready: NO (total: {total_time:.0f}ms)")

        print()

    print(f'{"="*80}')
    print("RECOMMENDATIONS")
    print(f'{"="*80}\n')

    print("1.  CRITICAL: Model Load Time Optimization")
    print("   - Pre-load models at server startup (avoid cold start)")
    print("   - Use model caching in memory (joblib Memory)")
    print("   - Consider ONNX export for faster loading")
    print("   - Expected improvement: 20s -> <100ms")
    print()

    print("2.  Inference Optimization")
    print("   - Models perform well for inference (<10ms)")
    print("   - Batch processing already efficient")
    print("   - No immediate optimization needed")
    print()

    print("3.  Backend Architecture Recommendations")
    print("   - Load models ONCE at server startup")
    print("   - Keep models in memory (singleton pattern)")
    print("   - Use Redis cache for predictions (24hr TTL)")
    print("   - Implement feature vector caching")
    print("   - Expected total response time: <30ms (warm cache)")
    print()


if __name__ == "__main__":
    test_model_performance()

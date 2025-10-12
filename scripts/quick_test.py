"""
🧪 QUICK SERVICE TEST
=====================

Tests all running services to verify they're working.
"""

import requests
import json
from datetime import datetime


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def test_service(name, url, expected_status=200):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"{Colors.GREEN}✅ {name:30} RUNNING on {url}{Colors.END}")
            return True
        else:
            print(
                f"{Colors.YELLOW}⚠️  {name:30} Status: {response.status_code}{Colors.END}"
            )
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ {name:30} NOT RESPONDING at {url}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ {name:30} ERROR: {e}{Colors.END}")
        return False


def test_ml_prediction(url_to_test="https://google.com"):
    """Test ML prediction endpoint"""
    print(f"\n{Colors.BLUE}🔍 Testing ML prediction with: {url_to_test}{Colors.END}")

    try:
        response = requests.post(
            "http://localhost:8000/api/predict", json={"url": url_to_test}, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ ML Prediction Successful!{Colors.END}")
            print(f"   URL: {data['url']}")
            print(f"   Is Phishing: {data['is_phishing']}")
            print(f"   Confidence: {data['confidence']:.2%}")
            print(f"   Threat Level: {data['threat_level']}")
            print(f"   Latency: {data['latency_ms']:.0f}ms")
            return True
        else:
            print(
                f"{Colors.RED}❌ ML Prediction Failed: Status {response.status_code}{Colors.END}"
            )
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ ML Prediction Error: {e}{Colors.END}")
        return False


def test_rust_api(url_to_test="https://google.com"):
    """Test Rust API endpoint"""
    print(f"\n{Colors.BLUE}🔍 Testing Rust API with: {url_to_test}{Colors.END}")

    try:
        response = requests.post(
            "http://localhost:8080/api/check-url", json={"url": url_to_test}, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✅ Rust API Successful!{Colors.END}")
            print(f"   URL: {data['url']}")
            print(f"   Is Phishing: {data['is_phishing']}")
            print(f"   Confidence: {data['confidence']:.2%}")
            print(f"   Threat Level: {data['threat_level']}")
            print(f"   Cached: {data.get('cached', False)}")
            print(f"   Latency: {data['latency_ms']:.0f}ms")
            return True
        else:
            print(
                f"{Colors.RED}❌ Rust API Failed: Status {response.status_code}{Colors.END}"
            )
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Rust API Error: {e}{Colors.END}")
        return False


def main():
    print_header("🧪 QUICK SERVICE TEST")

    print(f"{Colors.BOLD}Testing Services...{Colors.END}\n")

    # Test services
    results = {}

    results["python_ml"] = test_service(
        "Python ML Service", "http://localhost:8000/health"
    )
    results["rust_api"] = test_service(
        "Rust API Gateway", "http://localhost:8080/health"
    )
    results["redis"] = test_service(
        "Redis Cache", "http://localhost:6379", expected_status=None
    )

    # Test ML prediction if Python service is up
    if results["python_ml"]:
        results["ml_prediction"] = test_ml_prediction()

    # Test Rust API if it's up
    if results["rust_api"]:
        results["rust_check"] = test_rust_api()

    # Summary
    print_header("📊 TEST SUMMARY")

    services_up = sum(1 for v in results.values() if v)
    total_tests = len(results)

    print(f"Services Tested: {total_tests}")
    print(f"Services Up: {services_up}")
    print(f"Success Rate: {(services_up/total_tests)*100:.1f}%\n")

    if services_up == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL SERVICES ARE RUNNING!{Colors.END}")
        print(f"\n{Colors.GREEN}🎉 System is ready to use!{Colors.END}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
        print(f"   1. Run full integration tests: python3 integration_test.py")
        print(
            f"   2. Update Chrome extension to use: http://localhost:8080/api/check-url"
        )
        print(f"   3. (Optional) Retrain models: python3 train_real_data.py")
    elif results.get("python_ml"):
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  PARTIAL SUCCESS{Colors.END}")
        print(f"\n{Colors.GREEN}✅ Python ML Service is running!{Colors.END}")
        print(
            f"{Colors.YELLOW}   You can use the system without Redis/Rust (slower, no caching){Colors.END}"
        )
        print(f"\n{Colors.BLUE}To start missing services:{Colors.END}")
        if not results.get("redis"):
            print(
                f"   Redis: docker run -d --name phishing-redis -p 6379:6379 redis:alpine"
            )
        if not results.get("rust_api"):
            print(f"   Rust:  cd backend && cargo run --release")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ CRITICAL SERVICES NOT RUNNING{Colors.END}")
        print(f"\n{Colors.YELLOW}Start services with:{Colors.END}")
        print(f"   bash start_all_services.sh")
        print(f"\n{Colors.YELLOW}Or manually:{Colors.END}")
        print(f"   cd ml-service && python3 app.py")


if __name__ == "__main__":
    main()

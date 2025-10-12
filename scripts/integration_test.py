"""
🧪 END-TO-END INTEGRATION TESTING
==================================

Tests complete flow: Chrome Extension → Rust API → Python ML → Redis

Test Coverage:
- Health checks for all services
- URL checking (phishing & legitimate)
- Cache hit/miss behavior
- Error handling
- Performance benchmarks
"""

import requests
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime
import statistics


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


class IntegrationTester:
    def __init__(self):
        self.rust_api_url = "http://localhost:8080"
        self.python_ml_url = "http://localhost:8000"
        self.redis_url = "redis://localhost:6379"

        self.results = {"total_tests": 0, "passed": 0, "failed": 0, "errors": []}

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result"""
        self.results["total_tests"] += 1

        if status == "PASS":
            self.results["passed"] += 1
            icon = "✅"
            color = Colors.GREEN
        elif status == "FAIL":
            self.results["failed"] += 1
            icon = "❌"
            color = Colors.RED
            self.results["errors"].append(f"{name}: {details}")
        else:
            icon = "⚠️"
            color = Colors.YELLOW

        print(f"{icon} {color}{name:50}{Colors.END} [{status}] {details}")

    def test_service_health(self, name: str, url: str) -> bool:
        """Test if service is healthy"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.print_test(
                    f"{name} Health Check", "PASS", f"{response.status_code}"
                )
                return True
            else:
                self.print_test(
                    f"{name} Health Check", "FAIL", f"Status {response.status_code}"
                )
                return False
        except Exception as e:
            self.print_test(f"{name} Health Check", "FAIL", str(e))
            return False

    def test_url_check(self, url: str, expected_phishing: bool) -> Tuple[bool, float]:
        """Test URL checking"""
        try:
            start = time.time()
            response = requests.post(
                f"{self.rust_api_url}/api/check-url", json={"url": url}, timeout=15
            )
            latency = (time.time() - start) * 1000

            if response.status_code != 200:
                self.print_test(
                    f"Check URL: {url[:40]}", "FAIL", f"Status {response.status_code}"
                )
                return False, latency

            data = response.json()
            is_phishing = data["is_phishing"]
            confidence = data["confidence"]
            cached = data.get("cached", False)

            # Check if prediction matches expectation
            correct = is_phishing == expected_phishing
            status = "PASS" if correct else "FAIL"

            cache_indicator = "💾" if cached else "🔍"
            details = f"{cache_indicator} {data['threat_level']} ({confidence:.2f}) {latency:.0f}ms"

            self.print_test(f"Check URL: {url[:40]}", status, details)
            return correct, latency

        except Exception as e:
            self.print_test(f"Check URL: {url[:40]}", "FAIL", str(e))
            return False, 0

    def test_cache_behavior(self, url: str):
        """Test that caching works correctly"""
        print(f"\n{Colors.BLUE}Testing Cache Behavior for: {url[:50]}{Colors.END}")

        # First request (cache miss)
        start1 = time.time()
        response1 = requests.post(
            f"{self.rust_api_url}/api/check-url", json={"url": url}, timeout=15
        )
        latency1 = (time.time() - start1) * 1000
        cached1 = response1.json().get("cached", False)

        # Second request (should be cache hit)
        time.sleep(0.1)  # Small delay
        start2 = time.time()
        response2 = requests.post(
            f"{self.rust_api_url}/api/check-url", json={"url": url}, timeout=15
        )
        latency2 = (time.time() - start2) * 1000
        cached2 = response2.json().get("cached", False)

        # Verify caching
        if not cached1 and cached2:
            speedup = latency1 / latency2 if latency2 > 0 else 0
            self.print_test(
                "Cache Miss → Cache Hit",
                "PASS",
                f"1st: {latency1:.0f}ms, 2nd: {latency2:.0f}ms ({speedup:.1f}x faster)",
            )
        else:
            self.print_test(
                "Cache Miss → Cache Hit",
                "FAIL",
                f"1st cached={cached1}, 2nd cached={cached2}",
            )

    def test_concurrent_requests(self, num_requests: int = 10):
        """Test handling of concurrent requests"""
        import concurrent.futures

        print(f"\n{Colors.BLUE}Testing {num_requests} Concurrent Requests{Colors.END}")

        test_url = "https://google.com"

        def make_request():
            start = time.time()
            try:
                response = requests.post(
                    f"{self.rust_api_url}/api/check-url",
                    json={"url": test_url},
                    timeout=10,
                )
                latency = (time.time() - start) * 1000
                return response.status_code == 200, latency
            except:
                return False, 0

        start_all = time.time()
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_requests
        ) as executor:
            results = list(executor.map(lambda _: make_request(), range(num_requests)))

        total_time = (time.time() - start_all) * 1000
        successes = sum(1 for success, _ in results if success)
        latencies = [lat for success, lat in results if success]

        if latencies:
            avg_latency = statistics.mean(latencies)
            p99_latency = (
                statistics.quantiles(latencies, n=100)[98]
                if len(latencies) > 10
                else max(latencies)
            )

            details = f"{successes}/{num_requests} success, avg {avg_latency:.0f}ms, P99 {p99_latency:.0f}ms"
            status = "PASS" if successes == num_requests else "FAIL"
            self.print_test("Concurrent Requests", status, details)
        else:
            self.print_test("Concurrent Requests", "FAIL", "All requests failed")

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print(f"\n{Colors.BLUE}Testing Error Handling{Colors.END}")

        test_cases = [
            ("", "Empty URL"),
            ("short", "Too short URL"),
            ("not-a-url", "Invalid format"),
        ]

        for invalid_url, description in test_cases:
            try:
                response = requests.post(
                    f"{self.rust_api_url}/api/check-url",
                    json={"url": invalid_url},
                    timeout=5,
                )
                # Should return 400 Bad Request
                if 400 <= response.status_code < 500:
                    self.print_test(
                        f"Error Handling: {description}",
                        "PASS",
                        f"Correctly rejected with {response.status_code}",
                    )
                else:
                    self.print_test(
                        f"Error Handling: {description}",
                        "FAIL",
                        f"Unexpected status {response.status_code}",
                    )
            except Exception as e:
                self.print_test(f"Error Handling: {description}", "FAIL", str(e))

    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header("🧪 END-TO-END INTEGRATION TESTING")

        # Test 1: Service Health Checks
        self.print_header("1. SERVICE HEALTH CHECKS")
        rust_healthy = self.test_service_health(
            "Rust API Gateway", f"{self.rust_api_url}/health"
        )
        python_healthy = self.test_service_health(
            "Python ML Service", f"{self.python_ml_url}/health"
        )

        if not rust_healthy or not python_healthy:
            print(
                f"\n{Colors.RED}❌ Services not healthy. Cannot continue tests.{Colors.END}"
            )
            print(
                f"\n{Colors.YELLOW}💡 Make sure all services are running:{Colors.END}"
            )
            print(
                f"   1. Redis: docker run -d --name phishing-redis -p 6379:6379 redis:alpine"
            )
            print(f"   2. Python ML: cd ml-service && python3 app.py")
            print(f"   3. Rust API: cd backend && cargo run")
            return

        # Test 2: Legitimate URLs
        self.print_header("2. TESTING LEGITIMATE URLS")
        legitimate_urls = [
            "https://google.com",
            "https://github.com",
            "https://microsoft.com",
            "https://amazon.com",
            "https://wikipedia.org",
        ]

        for url in legitimate_urls:
            self.test_url_check(url, expected_phishing=False)

        # Test 3: Known Phishing URLs
        self.print_header("3. TESTING PHISHING URLS")
        phishing_urls = [
            "http://paypal-secure-login.tk/verify",
            "http://apple-id-verify.com/signin",
            "http://microsft-security.net/login",
        ]

        for url in phishing_urls:
            self.test_url_check(url, expected_phishing=True)

        # Test 4: Cache Behavior
        self.print_header("4. TESTING CACHE BEHAVIOR")
        self.test_cache_behavior("https://example.com")

        # Test 5: Concurrent Requests
        self.print_header("5. TESTING CONCURRENT REQUESTS")
        self.test_concurrent_requests(num_requests=20)

        # Test 6: Error Handling
        self.print_header("6. TESTING ERROR HANDLING")
        self.test_error_handling()

        # Test 7: Performance Benchmarks
        self.print_header("7. PERFORMANCE BENCHMARKS")
        self.run_performance_tests()

        # Final Summary
        self.print_summary()

    def run_performance_tests(self):
        """Run performance benchmarks"""
        test_url = "https://google.com"
        num_tests = 50

        print(f"Running {num_tests} requests to measure performance...")

        latencies = []
        cache_hits = 0

        for i in range(num_tests):
            start = time.time()
            response = requests.post(
                f"{self.rust_api_url}/api/check-url", json={"url": test_url}, timeout=10
            )
            latency = (time.time() - start) * 1000
            latencies.append(latency)

            if response.status_code == 200:
                data = response.json()
                if data.get("cached", False):
                    cache_hits += 1

        if latencies:
            avg = statistics.mean(latencies)
            median = statistics.median(latencies)
            p95 = (
                statistics.quantiles(latencies, n=100)[94]
                if len(latencies) > 10
                else max(latencies)
            )
            p99 = (
                statistics.quantiles(latencies, n=100)[98]
                if len(latencies) > 10
                else max(latencies)
            )
            cache_hit_rate = (cache_hits / num_tests) * 100

            print(f"\n{Colors.BLUE}Performance Results:{Colors.END}")
            print(f"  Average Latency: {avg:.1f}ms")
            print(f"  Median Latency:  {median:.1f}ms")
            print(f"  P95 Latency:     {p95:.1f}ms")
            print(f"  P99 Latency:     {p99:.1f}ms")
            print(f"  Cache Hit Rate:  {cache_hit_rate:.1f}%")

            # Performance targets
            targets_met = []
            if p99 < 200:
                targets_met.append("✅ P99 < 200ms")
            else:
                targets_met.append(f"❌ P99 {p99:.0f}ms (target: <200ms)")

            if cache_hit_rate > 80:
                targets_met.append("✅ Cache hit rate > 80%")
            else:
                targets_met.append(
                    f"⚠️  Cache hit rate {cache_hit_rate:.1f}% (target: >80%)"
                )

            print(f"\n{Colors.BLUE}Performance Targets:{Colors.END}")
            for target in targets_met:
                print(f"  {target}")

    def print_summary(self):
        """Print final test summary"""
        self.print_header("📊 TEST SUMMARY")

        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"{Colors.BOLD}Total Tests:{Colors.END}  {total}")
        print(f"{Colors.GREEN}Passed:{Colors.END}      {passed}")
        print(f"{Colors.RED}Failed:{Colors.END}      {failed}")
        print(f"{Colors.BLUE}Pass Rate:{Colors.END}   {pass_rate:.1f}%")

        if failed > 0:
            print(f"\n{Colors.RED}❌ Failed Tests:{Colors.END}")
            for error in self.results["errors"]:
                print(f"   • {error}")

        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")

        if pass_rate == 100:
            print(
                f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED! System is ready for production.{Colors.END}"
            )
        elif pass_rate >= 80:
            print(
                f"{Colors.YELLOW}⚠️  MOST TESTS PASSED. Review failures before production.{Colors.END}"
            )
        else:
            print(
                f"{Colors.RED}❌ MANY TESTS FAILED. System needs fixes before production.{Colors.END}"
            )


if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_all_tests()

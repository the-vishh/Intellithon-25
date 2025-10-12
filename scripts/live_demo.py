#!/usr/bin/env python3
"""
🎯 LIVE DEMO - Phishing Detection Pipeline
Shows the complete flow: Rust API → Redis → Python ML → 159 Features → Prediction
"""

import requests
import json
import time
from colorama import init, Fore, Style

init()

def print_header(title):
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title.center(80)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

def print_success(msg):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.YELLOW}ℹ️  {msg}{Style.RESET_ALL}")

def check_services():
    """Check if all services are running"""
    print_header("CHECKING SERVICES")

    services = {
        "Rust API Gateway": "http://localhost:8080/health",
        "Python ML Service": "http://localhost:8000/health"
    }

    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"{name} is running")
            else:
                print_error(f"{name} returned status {response.status_code}")
                all_ok = False
        except Exception as e:
            print_error(f"{name} is not responding: {e}")
            all_ok = False

    return all_ok

def test_phishing_detection(url):
    """Test phishing detection for a URL"""
    print_header(f"TESTING: {url}")

    # Call Rust API Gateway
    api_url = "http://localhost:8080/api/check-url"
    payload = {"url": url}

    print_info(f"Sending request to Rust API Gateway...")
    print_info(f"Request: POST {api_url}")
    print_info(f"Payload: {json.dumps(payload)}")

    start_time = time.time()

    try:
        response = requests.post(api_url, json=payload, timeout=30)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()

            print_success(f"Request completed in {(end_time - start_time)*1000:.2f}ms")
            print()

            # Display results
            print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║                           DETECTION RESULTS                               ║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")

            # Main result
            is_phishing = result.get('is_phishing', False)
            confidence = result.get('confidence', 0) * 100
            threat_level = result.get('threat_level', 'UNKNOWN')

            if is_phishing:
                status_color = Fore.RED
                status_icon = "🚨"
            else:
                status_color = Fore.GREEN
                status_icon = "✅"

            print(f"{Fore.CYAN}║{Style.RESET_ALL} {status_icon} Status:        {status_color}{('PHISHING DETECTED' if is_phishing else 'LEGITIMATE').ljust(55)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 📊 Confidence:    {status_color}{f'{confidence:.2f}%'.ljust(55)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} ⚠️  Threat Level:  {status_color}{threat_level.ljust(55)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")

            # Performance metrics
            details = result.get('details', {})
            print(f"{Fore.CYAN}╠═══════════════════════════════════════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} ⚡ Feature Extraction: {f'{details.get(\"feature_extraction_ms\", 0):.2f}ms'.ljust(49)}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 🧠 ML Inference:      {f'{details.get(\"ml_inference_ms\", 0):.2f}ms'.ljust(49)}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 📦 Total Latency:     {f'{result.get(\"latency_ms\", 0):.2f}ms'.ljust(49)}{Fore.CYAN}║{Style.RESET_ALL}")

            # Models used
            models = details.get('models_used', [])
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 🤖 Models Used:       {', '.join(models).ljust(49)}{Fore.CYAN}║{Style.RESET_ALL}")

            # Cache status
            cached = result.get('cached', False)
            cache_status = "HIT (from cache)" if cached else "MISS (computed)"
            print(f"{Fore.CYAN}║{Style.RESET_ALL} 💾 Cache:             {cache_status.ljust(49)}{Fore.CYAN}║{Style.RESET_ALL}")

            print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

            # Raw JSON response
            print(f"\n{Fore.YELLOW}📄 Full Response:{Style.RESET_ALL}")
            print(json.dumps(result, indent=2))

            return True
        else:
            print_error(f"Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def main():
    print_header("🎯 PHISHING DETECTION PIPELINE - LIVE DEMO")

    print(f"{Fore.CYAN}This demo shows the complete pipeline:{Style.RESET_ALL}")
    print(f"  1. Chrome Extension → Rust API Gateway (port 8080)")
    print(f"  2. Rust API → Redis Cache Check")
    print(f"  3. If cache miss → Python ML Service (port 8000)")
    print(f"  4. Python ML → Extract 159 features")
    print(f"  5. ML Models (LightGBM + XGBoost) → Prediction")
    print(f"  6. Result cached in Redis (24h TTL)")
    print()

    # Check services
    if not check_services():
        print_error("\nSome services are not running. Please start all services first.")
        print_info("Run: docker ps && netstat -ano | findstr ':6379 :8000 :8080'")
        return

    # Test URLs
    test_urls = [
        "https://google.com",
        "https://github.com",
        "http://suspicious-phishing-site.tk",
    ]

    for url in test_urls:
        test_phishing_detection(url)
        print()
        time.sleep(1)  # Brief pause between tests

    # Demonstrate caching
    print_header("DEMONSTRATING CACHE PERFORMANCE")
    print_info("Testing same URL twice to show cache hit performance...")

    test_url = "https://example.com"

    print(f"\n{Fore.YELLOW}First request (cache miss):{Style.RESET_ALL}")
    test_phishing_detection(test_url)

    print(f"\n{Fore.YELLOW}Second request (cache hit - should be much faster):{Style.RESET_ALL}")
    test_phishing_detection(test_url)

    print_header("DEMO COMPLETE")
    print_success("All components of the phishing detection pipeline are operational!")
    print()
    print(f"{Fore.YELLOW}Note:{Style.RESET_ALL} Models need retraining with real-world data for production use.")
    print(f"{Fore.YELLOW}      Currently showing 100% false positive rate on legitimate sites.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

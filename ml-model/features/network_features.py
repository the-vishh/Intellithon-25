"""
 NETWORK FEATURE EXTRACTOR
============================

Extract 20+ network and infrastructure features with HIGHEST quality
"""

import socket
import requests
from urllib.parse import urlparse
from typing import Dict, Any
import time


class NetworkFeatureExtractor:
    """
    High-performance network feature extraction

    Extracts 20+ features:
    - Response times
    - Server information
    - Redirect patterns
    - Geographic indicators
    - Port analysis
    - And more...
    """

    def __init__(self, timeout=5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def extract_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all network features from URL

        Args:
            url: URL to analyze

        Returns:
            Dictionary with 20+ network features
        """
        features = {}

        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(":")[0] if parsed.netloc else ""

            if not hostname:
                return self._get_default_features()

            # DNS Resolution Features (3 features)
            features["dns_resolves"] = self._check_dns_resolution(hostname)
            features["dns_resolution_time"] = self._measure_dns_time(hostname)
            features["has_multiple_ips"] = self._check_multiple_ips(hostname)

            # HTTP Response Features (5 features)
            response_data = self._get_http_response(url)
            features["http_response_time"] = response_data["response_time"]
            features["http_status_code"] = response_data["status_code"]
            features["http_redirects"] = response_data["redirect_count"]
            features["http_content_length"] = response_data["content_length"]
            features["http_response_code_category"] = self._categorize_status(
                response_data["status_code"]
            )

            # Server Features (5 features)
            features["server_header_present"] = response_data["has_server_header"]
            features["server_is_known"] = response_data["is_known_server"]
            features["x_powered_by_present"] = response_data["has_powered_by"]
            features["server_header_length"] = response_data["server_header_length"]
            features["suspicious_headers"] = response_data["suspicious_headers_count"]

            # Security Headers (5 features)
            features["has_security_headers"] = response_data["security_headers_count"]
            features["has_hsts"] = response_data["has_hsts"]
            features["has_csp"] = response_data["has_csp"]
            features["has_x_frame_options"] = response_data["has_x_frame"]
            features["has_x_content_type_options"] = response_data["has_x_content_type"]

            # Port and Protocol (2 features)
            features["uses_standard_port"] = self._check_standard_port(parsed)
            features["protocol_version"] = self._get_protocol_version(
                response_data["http_version"]
            )

        except Exception as e:
            features = self._get_default_features()

        return features

    def _get_default_features(self) -> Dict[str, Any]:
        """Default feature values"""
        return {
            # DNS
            "dns_resolves": 0,
            "dns_resolution_time": -1.0,
            "has_multiple_ips": 0,
            # HTTP Response
            "http_response_time": -1.0,
            "http_status_code": 0,
            "http_redirects": 0,
            "http_content_length": 0,
            "http_response_code_category": 0,
            # Server
            "server_header_present": 0,
            "server_is_known": 0,
            "x_powered_by_present": 0,
            "server_header_length": 0,
            "suspicious_headers": 0,
            # Security Headers
            "has_security_headers": 0,
            "has_hsts": 0,
            "has_csp": 0,
            "has_x_frame_options": 0,
            "has_x_content_type_options": 0,
            # Port/Protocol
            "uses_standard_port": 1,
            "protocol_version": 0,
        }

    def _check_dns_resolution(self, hostname: str) -> int:
        """Check if hostname resolves"""
        try:
            socket.gethostbyname(hostname)
            return 1
        except:
            return 0

    def _measure_dns_time(self, hostname: str) -> float:
        """Measure DNS resolution time in milliseconds"""
        try:
            start = time.time()
            socket.gethostbyname(hostname)
            end = time.time()
            return (end - start) * 1000  # Convert to ms
        except:
            return -1.0

    def _check_multiple_ips(self, hostname: str) -> int:
        """Check if hostname resolves to multiple IPs"""
        try:
            result = socket.getaddrinfo(hostname, None)
            unique_ips = set([addr[4][0] for addr in result])
            return 1 if len(unique_ips) > 1 else 0
        except:
            return 0

    def _get_http_response(self, url: str) -> Dict[str, Any]:
        """Get HTTP response and extract features"""
        data = {
            "response_time": -1.0,
            "status_code": 0,
            "redirect_count": 0,
            "content_length": 0,
            "has_server_header": 0,
            "is_known_server": 0,
            "has_powered_by": 0,
            "server_header_length": 0,
            "suspicious_headers_count": 0,
            "security_headers_count": 0,
            "has_hsts": 0,
            "has_csp": 0,
            "has_x_frame": 0,
            "has_x_content_type": 0,
            "http_version": "",
        }

        try:
            start = time.time()
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            end = time.time()

            data["response_time"] = (end - start) * 1000  # ms
            data["status_code"] = response.status_code
            data["redirect_count"] = len(response.history)
            data["content_length"] = len(response.content) if response.content else 0

            # Server headers
            server = response.headers.get("Server", "")
            if server:
                data["has_server_header"] = 1
                data["server_header_length"] = len(server)

                # Check for known servers
                known_servers = [
                    "nginx",
                    "apache",
                    "iis",
                    "cloudflare",
                    "amazon",
                    "microsoft",
                    "google",
                ]
                data["is_known_server"] = (
                    1 if any(s in server.lower() for s in known_servers) else 0
                )

            # X-Powered-By
            data["has_powered_by"] = 1 if response.headers.get("X-Powered-By") else 0

            # Security headers
            security_headers = [
                "Strict-Transport-Security",
                "Content-Security-Policy",
                "X-Frame-Options",
                "X-Content-Type-Options",
                "X-XSS-Protection",
            ]

            data["security_headers_count"] = sum(
                1 for h in security_headers if h in response.headers
            )
            data["has_hsts"] = (
                1 if "Strict-Transport-Security" in response.headers else 0
            )
            data["has_csp"] = 1 if "Content-Security-Policy" in response.headers else 0
            data["has_x_frame"] = 1 if "X-Frame-Options" in response.headers else 0
            data["has_x_content_type"] = (
                1 if "X-Content-Type-Options" in response.headers else 0
            )

            # Suspicious headers
            suspicious = ["X-Runtime", "X-AspNet-Version", "X-AspNetMvc-Version"]
            data["suspicious_headers_count"] = sum(
                1 for h in suspicious if h in response.headers
            )

            # HTTP version
            data["http_version"] = (
                str(response.raw.version) if hasattr(response.raw, "version") else "11"
            )

        except Exception as e:
            pass

        return data

    def _categorize_status(self, status_code: int) -> int:
        """Categorize HTTP status code"""
        if status_code == 0:
            return 0
        elif 200 <= status_code < 300:
            return 2  # Success
        elif 300 <= status_code < 400:
            return 3  # Redirect
        elif 400 <= status_code < 500:
            return 4  # Client error
        elif 500 <= status_code < 600:
            return 5  # Server error
        return 0

    def _check_standard_port(self, parsed) -> int:
        """Check if using standard port"""
        if ":" not in parsed.netloc:
            return 1  # No port specified = standard

        port_str = parsed.netloc.split(":")[-1]
        try:
            port = int(port_str)
            standard_ports = [80, 443, 8080, 8443]
            return 1 if port in standard_ports else 0
        except:
            return 1

    def _get_protocol_version(self, http_version: str) -> int:
        """Convert HTTP version to numeric score"""
        if "2" in http_version or "20" in http_version:
            return 2  # HTTP/2
        elif "11" in http_version:
            return 1  # HTTP/1.1
        elif "10" in http_version:
            return 0  # HTTP/1.0
        return 1  # Default to 1.1

    def get_feature_names(self) -> list:
        """Get list of all feature names"""
        return list(self._get_default_features().keys())

    def get_feature_count(self) -> int:
        """Get total number of features"""
        return len(self._get_default_features())


def demo_network_features():
    """Demonstrate network feature extraction"""
    print("=" * 80)
    print(" NETWORK FEATURE EXTRACTOR DEMO")
    print("=" * 80)

    extractor = NetworkFeatureExtractor()

    # Test URLs
    test_urls = [
        "https://google.com",
        "https://github.com",
    ]

    print(f"\n Extracting {extractor.get_feature_count()} network features...\n")

    for url in test_urls:
        print(f" URL: {url}")
        print("-" * 80)

        features = extractor.extract_features(url)

        # Print key features
        print(f"   DNS Resolves: {' Yes' if features['dns_resolves'] else ' No'}")
        print(f"   DNS Time: {features['dns_resolution_time']:.2f} ms")
        print(f"   HTTP Response Time: {features['http_response_time']:.2f} ms")
        print(f"   Status Code: {features['http_status_code']}")
        print(f"   Redirects: {features['http_redirects']}")
        print(f"   Security Headers: {features['has_security_headers']}")
        print(f"   HSTS: {' Yes' if features['has_hsts'] else ' No'}")
        print(
            f"   Known Server: {' Yes' if features['server_is_known'] else ' No'}"
        )
        print()

    print("=" * 80)
    print(f" NETWORK FEATURE EXTRACTION COMPLETE")
    print(f"   Total Features: {extractor.get_feature_count()}")
    print("=" * 80)


if __name__ == "__main__":
    demo_network_features()

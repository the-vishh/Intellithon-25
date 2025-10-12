"""
SSL/TLS Certificate Feature Extraction Module - 20+ Advanced Features
Analyzes SSL certificates, chain of trust, and security indicators
"""

import ssl
import socket
import OpenSSL
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, Any
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend


class SSLFeatureExtractor:
    """Extract 20+ SSL/TLS certificate features for phishing detection"""

    def __init__(self):
        self.trusted_cas = [
            "Let's Encrypt",
            "DigiCert",
            "Comodo",
            "GeoTrust",
            "Thawte",
            "RapidSSL",
            "GlobalSign",
            "Entrust",
            "Sectigo",
            "GoDaddy",
            "Amazon",
            "Microsoft",
            "Google Trust Services",
        ]

        self.timeout = 10

    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all 20 SSL/TLS features

        Returns:
            Dictionary with 20 SSL features
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(":")[0]

            if not hostname or parsed.scheme != "https":
                return self._get_no_ssl_features()

            # Get certificate
            cert_dict, cert_pem = self._get_certificate(hostname)

            if not cert_dict:
                return self._get_no_ssl_features()

            features = {}

            # Parse certificate
            cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())

            # ===== BASIC CERTIFICATE INFO (1-5) =====
            features["has_ssl"] = 1
            features["ssl_version"] = self._get_ssl_version(hostname)

            # Certificate validity
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
            now = datetime.now(timezone.utc)

            features["cert_is_valid"] = 1 if not_before <= now <= not_after else 0
            features["cert_age_days"] = (now - not_before).days
            features["cert_remaining_days"] = (not_after - now).days

            # ===== ISSUER ANALYSIS (6-10) =====
            issuer = cert.issuer.rfc4514_string()
            features["is_self_signed"] = self._is_self_signed(cert)
            features["is_trusted_ca"] = any(
                ca.lower() in issuer.lower() for ca in self.trusted_cas
            )
            features["issuer_length"] = len(issuer)

            # Extract issuer organization
            issuer_org = ""
            for attr in cert.issuer:
                if attr.oid == x509.NameOID.ORGANIZATION_NAME:
                    issuer_org = attr.value
                    break
            features["has_issuer_org"] = 1 if issuer_org else 0
            features["issuer_org_length"] = len(issuer_org)

            # ===== SUBJECT ANALYSIS (11-14) =====
            subject = cert.subject.rfc4514_string()
            features["subject_length"] = len(subject)

            # Extract subject fields
            subject_cn = ""
            subject_org = ""
            for attr in cert.subject:
                if attr.oid == x509.NameOID.COMMON_NAME:
                    subject_cn = attr.value
                elif attr.oid == x509.NameOID.ORGANIZATION_NAME:
                    subject_org = attr.value

            features["has_subject_cn"] = 1 if subject_cn else 0
            features["has_subject_org"] = 1 if subject_org else 0
            features["subject_cn_match_domain"] = (
                1 if subject_cn and hostname.lower() in subject_cn.lower() else 0
            )

            # ===== CERTIFICATE EXTENSIONS (15-18) =====
            try:
                # Subject Alternative Names (SAN)
                san_ext = cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                san_count = len(san_ext.value)
                features["san_count"] = san_count
                features["has_wildcard_san"] = any(
                    "*" in str(name) for name in san_ext.value
                )
            except x509.ExtensionNotFound:
                features["san_count"] = 0
                features["has_wildcard_san"] = 0

            # Extended Key Usage
            try:
                eku_ext = cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.EXTENDED_KEY_USAGE
                )
                features["has_server_auth"] = (
                    x509.oid.ExtendedKeyUsageOID.SERVER_AUTH in eku_ext.value
                )
            except x509.ExtensionNotFound:
                features["has_server_auth"] = 0

            # Certificate Policies
            try:
                cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.CERTIFICATE_POLICIES
                )
                features["has_cert_policies"] = 1
            except x509.ExtensionNotFound:
                features["has_cert_policies"] = 0

            # ===== SECURITY INDICATORS (19-20) =====
            features["key_size"] = cert.public_key().key_size
            features["signature_algorithm"] = self._get_signature_algorithm(cert)

            # ===== ADDITIONAL FEATURES (21-25) =====
            features["cert_serial_number_length"] = len(str(cert.serial_number))
            features["cert_version"] = cert.version.value

            # Certificate transparency
            try:
                cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS
                )
                features["has_cert_transparency"] = 1
            except x509.ExtensionNotFound:
                features["has_cert_transparency"] = 0

            # OCSP
            try:
                cert.extensions.get_extension_for_oid(
                    x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS
                )
                features["has_ocsp"] = 1
            except x509.ExtensionNotFound:
                features["has_ocsp"] = 0

            # Certificate chain depth
            features["cert_chain_depth"] = self._get_cert_chain_depth(hostname)

            return features

        except Exception as e:
            print(f"Error extracting SSL features: {e}")
            return self._get_no_ssl_features()

    def _get_certificate(self, hostname: str, port: int = 443):
        """Retrieve SSL certificate from hostname"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection(
                (hostname, port), timeout=self.timeout
            ) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_dict = ssock.getpeercert()
                    cert_pem = ssl.DER_cert_to_PEM_cert(
                        ssock.getpeercert(binary_form=True)
                    )

            return cert_dict, cert_pem

        except Exception as e:
            print(f"Error getting certificate for {hostname}: {e}")
            return None, None

    def _get_ssl_version(self, hostname: str, port: int = 443) -> int:
        """Get SSL/TLS version (higher is better)"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection(
                (hostname, port), timeout=self.timeout
            ) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    version = ssock.version()

                    # Map version to numeric value
                    version_map = {
                        "TLSv1.3": 4,
                        "TLSv1.2": 3,
                        "TLSv1.1": 2,
                        "TLSv1": 1,
                        "SSLv3": 0,
                    }
                    return version_map.get(version, 0)

        except Exception:
            return 0

    def _is_self_signed(self, cert) -> int:
        """Check if certificate is self-signed"""
        try:
            return 1 if cert.issuer == cert.subject else 0
        except Exception:
            return 0

    def _get_signature_algorithm(self, cert) -> int:
        """Get signature algorithm strength (higher is better)"""
        try:
            algo_name = cert.signature_algorithm_oid._name

            # Map algorithms to strength
            if "sha256" in algo_name.lower() or "sha384" in algo_name.lower():
                return 3
            elif "sha1" in algo_name.lower():
                return 2
            elif "md5" in algo_name.lower():
                return 1
            else:
                return 2  # Unknown, assume moderate

        except Exception:
            return 0

    def _get_cert_chain_depth(self, hostname: str, port: int = 443) -> int:
        """Get certificate chain depth"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection(
                (hostname, port), timeout=self.timeout
            ) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_chain = ssock.getpeercert_chain()
                    return len(cert_chain) if cert_chain else 0
        except Exception:
            return 0

    def _get_no_ssl_features(self) -> Dict[str, Any]:
        """Return features for URLs without SSL/HTTPS"""
        return {
            "has_ssl": 0,
            "ssl_version": 0,
            "cert_is_valid": 0,
            "cert_age_days": 0,
            "cert_remaining_days": 0,
            "is_self_signed": 0,
            "is_trusted_ca": 0,
            "issuer_length": 0,
            "has_issuer_org": 0,
            "issuer_org_length": 0,
            "subject_length": 0,
            "has_subject_cn": 0,
            "has_subject_org": 0,
            "subject_cn_match_domain": 0,
            "san_count": 0,
            "has_wildcard_san": 0,
            "has_server_auth": 0,
            "has_cert_policies": 0,
            "key_size": 0,
            "signature_algorithm": 0,
            "cert_serial_number_length": 0,
            "cert_version": 0,
            "has_cert_transparency": 0,
            "has_ocsp": 0,
            "cert_chain_depth": 0,
        }

    def get_feature_names(self) -> list:
        """Return list of all feature names"""
        return list(self._get_no_ssl_features().keys())


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    extractor = SSLFeatureExtractor()

    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "http://example.com",  # No HTTPS
        "https://self-signed.badssl.com",
        "https://expired.badssl.com",
    ]

    print("=" * 80)
    print("SSL/TLS FEATURE EXTRACTION TEST")
    print("=" * 80)

    for url in test_urls:
        print(f"\n URL: {url}")
        features = extractor.extract_all_features(url)

        print(f"\n Key SSL Features:")
        print(f"   Has SSL: {'Yes' if features['has_ssl'] else 'No'}")
        print(f"   Valid Certificate: {'Yes' if features['cert_is_valid'] else 'No'}")
        print(f"   Trusted CA: {'Yes' if features['is_trusted_ca'] else 'No'}")
        print(f"   Self-Signed: {'Yes' if features['is_self_signed'] else 'No'}")
        print(f"   Certificate Age: {features['cert_age_days']} days")
        print(f"   Key Size: {features['key_size']} bits")
        print(f"   Chain Depth: {features['cert_chain_depth']}")
        print("-" * 80)

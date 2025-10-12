"""
DNS & WHOIS Feature Extraction Module - 15+ Advanced Features
Analyzes domain registration, age, reputation, and DNS records
"""

import dns.resolver
import whois
from datetime import datetime, timezone
from urllib.parse import urlparse
import tldextract
from typing import Dict, Any
import socket


class DNSFeatureExtractor:
    """Extract 15+ DNS and WHOIS features for phishing detection"""

    def __init__(self):
        self.trusted_registrars = [
            "godaddy",
            "namecheap",
            "google",
            "cloudflare",
            "amazon",
            "markmonitor",
            "network solutions",
            "tucows",
            "enom",
        ]

        self.dns_servers = ["8.8.8.8", "1.1.1.1"]
        self.timeout = 10

    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all 15 DNS/WHOIS features

        Returns:
            Dictionary with 15 DNS features
        """
        try:
            parsed = urlparse(url)
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"

            features = {}

            # ===== WHOIS INFORMATION (1-6) =====
            whois_data = self._get_whois_data(domain)

            if whois_data:
                # Domain age
                creation_date = whois_data.get("creation_date")
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]

                if creation_date:
                    if isinstance(creation_date, str):
                        creation_date = datetime.fromisoformat(
                            creation_date.replace("Z", "+00:00")
                        )

                    domain_age_days = (
                        datetime.now(timezone.utc)
                        - creation_date.replace(tzinfo=timezone.utc)
                    ).days
                    features["domain_age_days"] = max(0, domain_age_days)
                else:
                    features["domain_age_days"] = 0

                # Expiration date
                expiration_date = whois_data.get("expiration_date")
                if isinstance(expiration_date, list):
                    expiration_date = expiration_date[0]

                if expiration_date:
                    if isinstance(expiration_date, str):
                        expiration_date = datetime.fromisoformat(
                            expiration_date.replace("Z", "+00:00")
                        )

                    days_until_expiration = (
                        expiration_date.replace(tzinfo=timezone.utc)
                        - datetime.now(timezone.utc)
                    ).days
                    features["days_until_expiration"] = max(0, days_until_expiration)
                else:
                    features["days_until_expiration"] = 0

                # Registrar
                registrar = whois_data.get("registrar", "").lower()
                features["is_trusted_registrar"] = any(
                    trusted in registrar for trusted in self.trusted_registrars
                )
                features["has_registrar"] = 1 if registrar else 0

                # WHOIS privacy
                features["has_whois_privacy"] = self._check_whois_privacy(whois_data)

                # Last updated
                updated_date = whois_data.get("updated_date")
                if isinstance(updated_date, list):
                    updated_date = updated_date[0]

                if updated_date:
                    if isinstance(updated_date, str):
                        updated_date = datetime.fromisoformat(
                            updated_date.replace("Z", "+00:00")
                        )

                    days_since_update = (
                        datetime.now(timezone.utc)
                        - updated_date.replace(tzinfo=timezone.utc)
                    ).days
                    features["days_since_last_update"] = max(0, days_since_update)
                else:
                    features["days_since_last_update"] = 0
            else:
                features["domain_age_days"] = 0
                features["days_until_expiration"] = 0
                features["is_trusted_registrar"] = 0
                features["has_registrar"] = 0
                features["has_whois_privacy"] = 0
                features["days_since_last_update"] = 0

            # ===== DNS RECORDS (7-12) =====
            dns_records = self._get_dns_records(domain)

            features["has_a_record"] = dns_records["a_count"] > 0
            features["has_mx_record"] = dns_records["mx_count"] > 0
            features["has_ns_record"] = dns_records["ns_count"] > 0
            features["a_record_count"] = dns_records["a_count"]
            features["mx_record_count"] = dns_records["mx_count"]
            features["ns_record_count"] = dns_records["ns_count"]

            # ===== ADDITIONAL FEATURES (13-15) =====
            features["has_txt_record"] = dns_records["txt_count"] > 0
            features["has_spf_record"] = dns_records["has_spf"]
            features["dns_query_time_ms"] = dns_records["query_time_ms"]

            return features

        except Exception as e:
            print(f"Error extracting DNS features: {e}")
            return self._get_default_features()

    def _get_whois_data(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        try:
            w = whois.whois(domain)
            return w if w else None
        except Exception as e:
            print(f"Error getting WHOIS data for {domain}: {e}")
            return None

    def _check_whois_privacy(self, whois_data: Dict[str, Any]) -> int:
        """Check if WHOIS privacy protection is enabled"""
        try:
            privacy_keywords = [
                "privacy",
                "private",
                "redacted",
                "protected",
                "whoisguard",
                "proxy",
                "masked",
            ]

            # Check registrant info
            registrant = str(whois_data.get("registrant", "")).lower()
            admin = str(whois_data.get("admin", "")).lower()

            return (
                1
                if any(kw in registrant or kw in admin for kw in privacy_keywords)
                else 0
            )
        except Exception:
            return 0

    def _get_dns_records(self, domain: str) -> Dict[str, Any]:
        """Get DNS record counts and types"""
        records = {
            "a_count": 0,
            "mx_count": 0,
            "ns_count": 0,
            "txt_count": 0,
            "has_spf": 0,
            "query_time_ms": 0,
        }

        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = self.dns_servers
            resolver.timeout = self.timeout
            resolver.lifetime = self.timeout

            start_time = datetime.now()

            # A records
            try:
                answers = resolver.resolve(domain, "A")
                records["a_count"] = len(answers)
            except Exception:
                pass

            # MX records
            try:
                answers = resolver.resolve(domain, "MX")
                records["mx_count"] = len(answers)
            except Exception:
                pass

            # NS records
            try:
                answers = resolver.resolve(domain, "NS")
                records["ns_count"] = len(answers)
            except Exception:
                pass

            # TXT records and SPF
            try:
                answers = resolver.resolve(domain, "TXT")
                records["txt_count"] = len(answers)

                # Check for SPF record
                for rdata in answers:
                    txt_string = str(rdata).lower()
                    if "v=spf1" in txt_string:
                        records["has_spf"] = 1
                        break
            except Exception:
                pass

            end_time = datetime.now()
            records["query_time_ms"] = int(
                (end_time - start_time).total_seconds() * 1000
            )

        except Exception as e:
            print(f"Error getting DNS records for {domain}: {e}")

        return records

    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features in case of error"""
        return {
            "domain_age_days": 0,
            "days_until_expiration": 0,
            "is_trusted_registrar": 0,
            "has_registrar": 0,
            "has_whois_privacy": 0,
            "days_since_last_update": 0,
            "has_a_record": 0,
            "has_mx_record": 0,
            "has_ns_record": 0,
            "a_record_count": 0,
            "mx_record_count": 0,
            "ns_record_count": 0,
            "has_txt_record": 0,
            "has_spf_record": 0,
            "dns_query_time_ms": 0,
        }

    def get_feature_names(self) -> list:
        """Return list of all feature names"""
        return list(self._get_default_features().keys())


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    extractor = DNSFeatureExtractor()

    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://brand-new-suspicious-domain.tk",
        "https://paypal-verify.online",
    ]

    print("=" * 80)
    print("DNS & WHOIS FEATURE EXTRACTION TEST")
    print("=" * 80)

    for url in test_urls:
        print(f"\n URL: {url}")
        features = extractor.extract_all_features(url)

        print(f"\n Key DNS Features:")
        print(f"   Domain Age: {features['domain_age_days']} days")
        print(f"   Days Until Expiration: {features['days_until_expiration']}")
        print(
            f"   Trusted Registrar: {'Yes' if features['is_trusted_registrar'] else 'No'}"
        )
        print(f"   WHOIS Privacy: {'Yes' if features['has_whois_privacy'] else 'No'}")
        print(f"   A Records: {features['a_record_count']}")
        print(f"   MX Records: {features['mx_record_count']}")
        print(f"   Has SPF: {'Yes' if features['has_spf_record'] else 'No'}")
        print(f"   DNS Query Time: {features['dns_query_time_ms']} ms")
        print("-" * 80)

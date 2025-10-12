"""
 API INTEGRATION TEST
Test threat intelligence APIs with your keys
"""

import os
import sys
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# Add parent to path
sys.path.append(os.path.dirname(__file__))

from utils.threat_intelligence import ThreatIntelligence


def test_apis():
    print("=" * 80)
    print(" TESTING API INTEGRATION")
    print("=" * 80)

    # Check environment variables
    print("\n Checking API Keys...")

    google_key = os.getenv("GOOGLE_SAFE_BROWSING_KEY")
    virustotal_key = os.getenv("VIRUSTOTAL_API_KEY")
    phishtank_key = os.getenv("PHISHTANK_API_KEY")

    print(f"   Google Safe Browsing: {' Configured' if google_key else ' Missing'}")
    print(f"   VirusTotal: {' Configured' if virustotal_key else ' Missing'}")
    print(
        f"   PhishTank: {' Configured' if phishtank_key else '  Optional (not set)'}"
    )

    # Initialize threat intelligence
    print("\n Initializing Threat Intelligence...")
    threat_intel = ThreatIntelligence()

    # Test URLs
    test_urls = [
        ("https://www.google.com", "Safe"),
        (
            "http://testsafebrowsing.appspot.com/s/malware.html",
            "Known Malware (Google Test)",
        ),
        ("http://malware.testing.google.test/testing/malware/", "Known Malware (Test)"),
    ]

    print("\n Testing Threat Detection...")
    print("=" * 80)

    for url, description in test_urls:
        print(f"\n Testing: {url}")
        print(f"   Description: {description}")

        try:
            result = threat_intel.check_url(url)

            print(f"    Is Threat: {' YES' if result['is_threat'] else ' NO'}")
            print(f"    Threat Score: {result['threat_score']:.2f}")
            print(f"    Sources: {', '.join(result['sources'])}")

            if result["details"]:
                print(f"    Details:")
                for detail in result["details"][:3]:  # Show first 3
                    print(f"      - {detail}")

        except Exception as e:
            print(f"    Error: {str(e)}")

    print("\n" + "=" * 80)
    print(" API INTEGRATION TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_apis()

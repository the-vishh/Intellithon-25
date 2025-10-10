"""
Content Feature Extraction Module - 40+ Advanced Features
Analyzes HTML content, forms, links, and text patterns
"""

from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, Any
import re
from collections import Counter


class ContentFeatureExtractor:
    """Extract 40+ content features from HTML for phishing detection"""

    def __init__(self):
        self.urgency_keywords = [
            "urgent",
            "immediate",
            "act now",
            "limited time",
            "expire",
            "suspended",
            "verify",
            "confirm",
            "click here",
            "security alert",
            "unusual activity",
            "locked",
            "update required",
            "action required",
        ]

        self.brand_names = [
            "paypal",
            "amazon",
            "apple",
            "microsoft",
            "google",
            "facebook",
            "netflix",
            "ebay",
            "bank",
            "wells fargo",
            "chase",
            "citibank",
        ]

        self.suspicious_form_fields = [
            "password",
            "credit",
            "card",
            "cvv",
            "ssn",
            "social",
            "security",
            "account",
            "pin",
            "routing",
            "bank",
        ]

        self.timeout = 15
        self.max_content_size = 5 * 1024 * 1024  # 5 MB

    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all 40 content features

        Returns:
            Dictionary with 40 content features
        """
        try:
            # Fetch HTML content
            html_content = self._fetch_html(url)

            if not html_content:
                return self._get_default_features()

            soup = BeautifulSoup(html_content, "html.parser")
            parsed_url = urlparse(url)
            base_domain = parsed_url.netloc

            features = {}

            # ===== BASIC HTML FEATURES (1-5) =====
            features["html_length"] = len(html_content)
            features["title_length"] = len(soup.title.string) if soup.title else 0
            features["has_title"] = 1 if soup.title and soup.title.string else 0
            features["meta_count"] = len(soup.find_all("meta"))
            features["script_count"] = len(soup.find_all("script"))

            # ===== LINK ANALYSIS (6-12) =====
            all_links = soup.find_all("a", href=True)
            features["link_count"] = len(all_links)

            # Analyze link destinations
            external_links = 0
            internal_links = 0
            empty_links = 0
            suspicious_links = 0

            for link in all_links:
                href = link["href"].strip()

                if not href or href == "#":
                    empty_links += 1
                    continue

                # Make absolute URL
                absolute_url = urljoin(url, href)
                link_domain = urlparse(absolute_url).netloc

                if link_domain and link_domain != base_domain:
                    external_links += 1
                else:
                    internal_links += 1

                # Check for suspicious patterns
                if any(
                    kw in href.lower()
                    for kw in ["login", "verify", "account", "secure"]
                ):
                    suspicious_links += 1

            total_links = len(all_links) if len(all_links) > 0 else 1
            features["external_link_count"] = external_links
            features["internal_link_count"] = internal_links
            features["empty_link_count"] = empty_links
            features["external_link_ratio"] = external_links / total_links
            features["empty_link_ratio"] = empty_links / total_links
            features["suspicious_link_count"] = suspicious_links

            # ===== FORM ANALYSIS (13-20) =====
            forms = soup.find_all("form")
            features["form_count"] = len(forms)
            features["has_forms"] = 1 if len(forms) > 0 else 0

            # Analyze form inputs
            input_fields = soup.find_all("input")
            features["input_field_count"] = len(input_fields)

            password_fields = 0
            hidden_fields = 0
            suspicious_fields = 0

            for inp in input_fields:
                input_type = inp.get("type", "").lower()
                input_name = inp.get("name", "").lower()
                input_id = inp.get("id", "").lower()

                if input_type == "password":
                    password_fields += 1

                if input_type == "hidden":
                    hidden_fields += 1

                # Check for suspicious field names
                if any(
                    sus in input_name or sus in input_id
                    for sus in self.suspicious_form_fields
                ):
                    suspicious_fields += 1

            features["password_field_count"] = password_fields
            features["hidden_field_count"] = hidden_fields
            features["suspicious_field_count"] = suspicious_fields

            # Form action analysis
            form_actions_external = 0
            for form in forms:
                action = form.get("action", "")
                if action:
                    action_url = urljoin(url, action)
                    action_domain = urlparse(action_url).netloc
                    if action_domain and action_domain != base_domain:
                        form_actions_external += 1

            features["external_form_action_count"] = form_actions_external

            # ===== TEXT CONTENT ANALYSIS (21-28) =====
            text_content = soup.get_text().lower()
            features["text_length"] = len(text_content)

            # Urgency keywords
            features["urgency_keyword_count"] = sum(
                text_content.count(kw) for kw in self.urgency_keywords
            )

            # Brand mentions
            features["brand_mention_count"] = sum(
                text_content.count(brand) for brand in self.brand_names
            )

            # Special characters in text
            special_char_count = sum(
                1 for c in text_content if not c.isalnum() and not c.isspace()
            )
            features["special_char_in_text_count"] = special_char_count

            # Repeated words (spam indicator)
            words = re.findall(r"\b\w+\b", text_content)
            if words:
                word_freq = Counter(words)
                most_common_word_count = (
                    word_freq.most_common(1)[0][1] if word_freq else 0
                )
                features["most_common_word_freq"] = most_common_word_count / len(words)
            else:
                features["most_common_word_freq"] = 0

            # Copyright notice
            features["has_copyright"] = (
                1 if "©" in html_content or "copyright" in text_content else 0
            )

            # Contact information
            features["has_email"] = (
                1
                if re.search(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text_content
                )
                else 0
            )
            features["has_phone"] = (
                1 if re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text_content) else 0
            )

            # ===== IFRAME & OBJECT ANALYSIS (29-32) =====
            iframes = soup.find_all("iframe")
            features["iframe_count"] = len(iframes)
            features["has_invisible_iframe"] = any(
                "hidden" in str(iframe.get("style", "")).lower()
                or iframe.get("width") == "0"
                or iframe.get("height") == "0"
                for iframe in iframes
            )

            objects = soup.find_all("object")
            features["object_count"] = len(objects)
            features["embed_count"] = len(soup.find_all("embed"))

            # ===== IMAGE ANALYSIS (33-36) =====
            images = soup.find_all("img")
            features["image_count"] = len(images)

            images_without_alt = sum(1 for img in images if not img.get("alt"))
            features["images_without_alt_count"] = images_without_alt

            external_images = 0
            for img in images:
                src = img.get("src", "")
                if src:
                    img_url = urljoin(url, src)
                    img_domain = urlparse(img_url).netloc
                    if img_domain and img_domain != base_domain:
                        external_images += 1

            features["external_image_count"] = external_images
            features["external_image_ratio"] = (
                external_images / len(images) if len(images) > 0 else 0
            )

            # ===== ADDITIONAL FEATURES (37-40) =====
            features["favicon_external"] = self._is_favicon_external(soup, base_domain)
            features["has_popup"] = self._has_popup_code(html_content)
            features["has_right_click_disabled"] = self._has_right_click_disabled(
                html_content
            )
            features["html_to_text_ratio"] = (
                len(text_content) / len(html_content) if len(html_content) > 0 else 0
            )

            return features

        except Exception as e:
            print(f"Error extracting content features: {e}")
            return self._get_default_features()

    def _fetch_html(self, url: str) -> str:
        """Fetch HTML content from URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True,
            )

            # Check content size
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_size:
                print(f"Content too large: {content_length} bytes")
                return None

            return response.text

        except Exception as e:
            print(f"Error fetching HTML from {url}: {e}")
            return None

    def _is_favicon_external(self, soup: BeautifulSoup, base_domain: str) -> int:
        """Check if favicon is loaded from external domain"""
        try:
            favicon = soup.find("link", rel="icon") or soup.find(
                "link", rel="shortcut icon"
            )
            if favicon and favicon.get("href"):
                favicon_url = favicon["href"]
                favicon_domain = urlparse(favicon_url).netloc
                return 1 if favicon_domain and favicon_domain != base_domain else 0
        except Exception:
            pass
        return 0

    def _has_popup_code(self, html_content: str) -> int:
        """Check for popup/alert code"""
        popup_patterns = ["window.open", "alert(", "prompt(", "confirm(", "popup"]
        return (
            1
            if any(pattern in html_content.lower() for pattern in popup_patterns)
            else 0
        )

    def _has_right_click_disabled(self, html_content: str) -> int:
        """Check if right-click is disabled (suspicious)"""
        patterns = ["oncontextmenu", "event.button==2", "contextmenu"]
        return 1 if any(pattern in html_content.lower() for pattern in patterns) else 0

    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features in case of error"""
        feature_names = [
            "html_length",
            "title_length",
            "has_title",
            "meta_count",
            "script_count",
            "link_count",
            "external_link_count",
            "internal_link_count",
            "empty_link_count",
            "external_link_ratio",
            "empty_link_ratio",
            "suspicious_link_count",
            "form_count",
            "has_forms",
            "input_field_count",
            "password_field_count",
            "hidden_field_count",
            "suspicious_field_count",
            "external_form_action_count",
            "text_length",
            "urgency_keyword_count",
            "brand_mention_count",
            "special_char_in_text_count",
            "most_common_word_freq",
            "has_copyright",
            "has_email",
            "has_phone",
            "iframe_count",
            "has_invisible_iframe",
            "object_count",
            "embed_count",
            "image_count",
            "images_without_alt_count",
            "external_image_count",
            "external_image_ratio",
            "favicon_external",
            "has_popup",
            "has_right_click_disabled",
            "html_to_text_ratio",
        ]
        return {name: 0 for name in feature_names}

    def get_feature_names(self) -> list:
        """Return list of all feature names"""
        return list(self._get_default_features().keys())


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == "__main__":
    extractor = ContentFeatureExtractor()

    test_urls = ["https://www.google.com", "https://www.github.com"]

    print("=" * 80)
    print("CONTENT FEATURE EXTRACTION TEST")
    print("=" * 80)

    for url in test_urls:
        print(f"\n📄 URL: {url}")
        features = extractor.extract_all_features(url)

        print(f"\n📊 Key Content Features:")
        print(f"   HTML Length: {features['html_length']} bytes")
        print(f"   Forms: {features['form_count']}")
        print(f"   Password Fields: {features['password_field_count']}")
        print(
            f"   External Links: {features['external_link_count']} ({features['external_link_ratio']:.2%})"
        )
        print(f"   Urgency Keywords: {features['urgency_keyword_count']}")
        print(f"   Brand Mentions: {features['brand_mention_count']}")
        print(f"   Has Popup Code: {'Yes' if features['has_popup'] else 'No'}")
        print("-" * 80)

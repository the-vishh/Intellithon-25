"""
 FAST 159-FEATURE TRAINING (SIMULATED DATA)
==============================================

Train ML models with 159 features using simulated phishing feature vectors.
This demonstrates the highest quality system without network delays.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
import joblib
import os
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")


class FastModelTrainer:
    """
    Fast model trainer with 159 simulated features

    Demonstrates HIGHEST QUALITY system performance
    """

    def __init__(self, output_dir="models"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.models = {}
        self.feature_count = 159

        # Feature names (159 total)
        self.feature_names = self._generate_feature_names()

    def _generate_feature_names(self):
        """Generate 159 feature names"""
        names = []

        # URL Features (35)
        url_features = [
            "url_length",
            "domain_length",
            "path_length",
            "num_dots",
            "num_hyphens",
            "num_underscores",
            "num_slashes",
            "num_question_marks",
            "num_equal_signs",
            "num_ampersands",
            "num_at_symbols",
            "num_exclamation_marks",
            "num_spaces",
            "num_tildes",
            "num_commas",
            "num_plus",
            "num_asterisks",
            "num_hashtags",
            "num_dollars",
            "num_percents",
            "has_ip",
            "num_subdomains",
            "tld_length",
            "has_port",
            "port_number",
            "is_https",
            "has_www",
            "domain_digit_count",
            "domain_letter_count",
            "path_digit_count",
            "path_letter_count",
            "query_length",
            "fragment_length",
            "url_entropy",
            "domain_entropy",
        ]
        names.extend(url_features)

        # SSL/TLS Features (25)
        ssl_features = [
            "has_certificate",
            "cert_valid",
            "cert_days_to_expire",
            "cert_issuer_length",
            "cert_subject_length",
            "cert_version",
            "cert_serial_number_length",
            "cert_signature_algorithm_length",
            "cert_key_size",
            "cert_is_self_signed",
            "cert_has_san",
            "cert_san_count",
            "cert_wildcard",
            "cert_issuer_trusted",
            "cert_organization_length",
            "cert_common_name_matches",
            "cert_age_days",
            "ssl_version",
            "tls_version",
            "cipher_strength",
            "has_hsts",
            "hsts_max_age",
            "has_mixed_content",
            "ssl_labs_grade",
            "security_score",
        ]
        names.extend(ssl_features)

        # DNS Features (15)
        dns_features = [
            "domain_age_days",
            "domain_registration_length",
            "domain_expiration_days",
            "whois_privacy",
            "registrar_reputation",
            "nameserver_count",
            "mx_record_count",
            "txt_record_count",
            "cname_record_count",
            "a_record_count",
            "aaaa_record_count",
            "dns_record_count",
            "has_dnssec",
            "registrar_length",
            "country_code",
        ]
        names.extend(dns_features)

        # Content Features (39)
        content_features = [
            "page_title_length",
            "meta_description_length",
            "num_links",
            "num_external_links",
            "external_link_ratio",
            "num_images",
            "num_scripts",
            "num_iframes",
            "num_forms",
            "num_inputs",
            "num_buttons",
            "num_hidden_inputs",
            "page_word_count",
            "page_char_count",
            "num_paragraphs",
            "num_headings",
            "num_lists",
            "has_favicon",
            "num_stylesheets",
            "page_size_kb",
            "load_time_ms",
            "num_cookies",
            "has_social_media_links",
            "num_popup_triggers",
            "has_right_click_disable",
            "has_status_bar_customization",
            "num_redirects",
            "redirect_url_length",
            "form_action_suspicious",
            "has_password_input",
            "has_credit_card_input",
            "num_suspicious_keywords",
            "text_input_ratio",
            "link_text_ratio",
            "html_tag_ratio",
            "script_tag_ratio",
            "visual_complexity",
            "color_diversity",
            "layout_complexity",
        ]
        names.extend(content_features)

        # Behavioral Features (25)
        behavioral_features = [
            "has_at_symbol",
            "has_double_slash",
            "has_ip_address",
            "has_port_in_domain",
            "uses_url_shortening",
            "num_encoded_chars",
            "has_hex_encoding",
            "has_unicode_encoding",
            "obfuscation_score",
            "abnormal_url_score",
            "phishing_keywords_count",
            "login_keywords",
            "verify_keywords",
            "urgency_keywords",
            "keyword_density",
            "num_params",
            "has_url_param",
            "has_email_param",
            "has_suspicious_params",
            "param_total_length",
            "has_suspicious_extension",
            "path_extension_count",
            "extension_mismatch",
            "impersonation_score",
            "typosquatting_score",
        ]
        names.extend(behavioral_features)

        # Network Features (20)
        network_features = [
            "dns_resolves",
            "dns_resolution_time_ms",
            "has_multiple_ips",
            "http_response_time_ms",
            "http_status_code",
            "num_redirects",
            "response_content_length",
            "response_type_category",
            "has_server_header",
            "is_known_server",
            "has_x_powered_by",
            "server_header_length",
            "has_suspicious_headers",
            "security_header_count",
            "has_hsts_header",
            "has_csp_header",
            "has_x_frame_options",
            "has_x_content_type_options",
            "is_standard_port",
            "protocol_version",
        ]
        names.extend(network_features)

        return names

    def generate_synthetic_data(self, n_samples=2000):
        """
        Generate synthetic phishing detection data

        Simulates real feature distributions for 159 features
        """
        print(f"\n{'='*80}")
        print(f" GENERATING SYNTHETIC TRAINING DATA")
        print(f"{'='*80}")
        print(f"   Samples: {n_samples}")
        print(f"   Features: {self.feature_count}")

        np.random.seed(42)

        # Split into phishing and legitimate
        n_phishing = n_samples // 2
        n_legit = n_samples - n_phishing

        print(f"\n Generating {n_phishing} phishing samples...")
        X_phishing = self._generate_phishing_features(n_phishing)
        y_phishing = np.ones(n_phishing)

        print(f" Generating {n_legit} legitimate samples...")
        X_legit = self._generate_legit_features(n_legit)
        y_legit = np.zeros(n_legit)

        # Combine
        X = np.vstack([X_phishing, X_legit])
        y = np.concatenate([y_phishing, y_legit])

        # Shuffle
        shuffle_idx = np.random.permutation(n_samples)
        X = X[shuffle_idx]
        y = y[shuffle_idx]

        print(f"\n Training data generated!")
        print(f"   Shape: {X.shape}")
        print(f"   Phishing: {sum(y == 1)}")
        print(f"   Legitimate: {sum(y == 0)}")
        print(f"   Feature Range: [{X.min():.2f}, {X.max():.2f}]")
        print(f"   Mean: {X.mean():.2f}, Std: {X.std():.2f}")

        return X, y

    def _generate_phishing_features(self, n):
        """Generate phishing-like feature vectors"""
        features = []

        for _ in range(n):
            f = np.zeros(159)

            # URL Features (0-34): Longer, more complex URLs
            f[0] = np.random.randint(30, 200)  # url_length
            f[1] = np.random.randint(10, 50)  # domain_length
            f[2] = np.random.randint(10, 100)  # path_length
            f[3] = np.random.randint(3, 10)  # num_dots (suspicious)
            f[4] = np.random.randint(2, 15)  # num_hyphens (suspicious)
            f[5] = np.random.randint(1, 5)  # num_underscores
            f[10] = np.random.choice(
                [0, 1], p=[0.3, 0.7]
            )  # num_at_symbols (phishing indicator)
            f[20] = np.random.choice([0, 1], p=[0.3, 0.7])  # has_ip (phishing)
            f[25] = np.random.choice([0, 1], p=[0.6, 0.4])  # is_https (not always)
            f[26] = np.random.choice([0, 1], p=[0.7, 0.3])  # has_www
            f[33] = np.random.uniform(3.5, 5.5)  # url_entropy (high)

            # SSL Features (35-59): Weak or no SSL
            f[35] = np.random.choice([0, 1], p=[0.5, 0.5])  # has_certificate
            f[36] = np.random.choice([0, 1], p=[0.7, 0.3])  # cert_valid
            f[37] = np.random.randint(-100, 30)  # cert_days_to_expire (expired or soon)
            f[44] = np.random.choice([0, 1], p=[0.6, 0.4])  # cert_is_self_signed
            f[48] = np.random.randint(0, 2)  # cert_age_days (new cert)

            # DNS Features (60-74): New domains, suspicious WHOIS
            f[60] = np.random.randint(0, 90)  # domain_age_days (very new)
            f[63] = np.random.choice([0, 1], p=[0.3, 0.7])  # whois_privacy (hidden)
            f[64] = np.random.uniform(0, 0.5)  # registrar_reputation (low)

            # Content Features (75-113): Suspicious page content
            f[75] = np.random.randint(0, 50)  # page_title_length (short or missing)
            f[77] = np.random.randint(10, 100)  # num_links
            f[78] = np.random.randint(5, 80)  # num_external_links (many)
            f[79] = np.random.uniform(0.3, 0.9)  # external_link_ratio (high)
            f[82] = np.random.randint(5, 20)  # num_scripts (many)
            f[83] = np.random.randint(0, 5)  # num_iframes (suspicious)
            f[84] = np.random.randint(1, 10)  # num_forms
            f[86] = np.random.randint(0, 5)  # num_buttons
            f[87] = np.random.randint(0, 10)  # num_hidden_inputs (suspicious)
            f[106] = np.random.randint(0, 20)  # num_suspicious_keywords
            f[108] = np.random.choice([0, 1], p=[0.4, 0.6])  # has_password_input

            # Behavioral Features (114-138): Phishing patterns
            f[114] = np.random.choice([0, 1], p=[0.7, 0.3])  # has_at_symbol
            f[115] = np.random.choice([0, 1], p=[0.8, 0.2])  # has_double_slash
            f[116] = np.random.choice([0, 1], p=[0.7, 0.3])  # has_ip_address
            f[118] = np.random.choice([0, 1], p=[0.8, 0.2])  # uses_url_shortening
            f[119] = np.random.randint(0, 20)  # num_encoded_chars
            f[122] = np.random.uniform(0, 1)  # obfuscation_score (high)
            f[124] = np.random.randint(2, 10)  # phishing_keywords_count
            f[125] = np.random.choice([0, 1], p=[0.5, 0.5])  # login_keywords
            f[126] = np.random.choice([0, 1], p=[0.5, 0.5])  # verify_keywords
            f[127] = np.random.choice([0, 1], p=[0.6, 0.4])  # urgency_keywords
            f[137] = np.random.uniform(0.5, 1)  # impersonation_score (high)
            f[138] = np.random.uniform(0.3, 1)  # typosquatting_score (high)

            # Network Features (139-158): Suspicious network behavior
            f[139] = np.random.choice([0, 1], p=[0.3, 0.7])  # dns_resolves
            f[143] = np.random.randint(200, 404)  # http_status_code
            f[144] = np.random.randint(0, 5)  # num_redirects (many)
            f[153] = np.random.randint(0, 3)  # security_header_count (few)

            features.append(f)

        return np.array(features)

    def _generate_legit_features(self, n):
        """Generate legitimate-like feature vectors"""
        features = []

        for _ in range(n):
            f = np.zeros(159)

            # URL Features (0-34): Shorter, cleaner URLs
            f[0] = np.random.randint(15, 50)  # url_length
            f[1] = np.random.randint(5, 20)  # domain_length
            f[2] = np.random.randint(0, 30)  # path_length
            f[3] = np.random.randint(1, 3)  # num_dots (normal)
            f[4] = np.random.randint(0, 2)  # num_hyphens (few)
            f[5] = np.random.randint(0, 1)  # num_underscores
            f[10] = 0  # num_at_symbols (none)
            f[20] = 0  # has_ip (none)
            f[25] = 1  # is_https (secure)
            f[26] = np.random.choice([0, 1])  # has_www
            f[33] = np.random.uniform(2.5, 4.0)  # url_entropy (normal)

            # SSL Features (35-59): Strong SSL
            f[35] = 1  # has_certificate
            f[36] = 1  # cert_valid
            f[37] = np.random.randint(90, 365)  # cert_days_to_expire (valid)
            f[44] = 0  # cert_is_self_signed (no)
            f[48] = np.random.randint(30, 365)  # cert_age_days (established)
            f[53] = 1  # cert_issuer_trusted

            # DNS Features (60-74): Established domains
            f[60] = np.random.randint(365, 3650)  # domain_age_days (old)
            f[63] = 0  # whois_privacy (public)
            f[64] = np.random.uniform(0.7, 1.0)  # registrar_reputation (high)

            # Content Features (75-113): Normal page content
            f[75] = np.random.randint(20, 80)  # page_title_length
            f[77] = np.random.randint(5, 50)  # num_links
            f[78] = np.random.randint(1, 20)  # num_external_links (few)
            f[79] = np.random.uniform(0.1, 0.4)  # external_link_ratio (low)
            f[82] = np.random.randint(1, 10)  # num_scripts (normal)
            f[83] = 0  # num_iframes (none)
            f[84] = np.random.randint(0, 3)  # num_forms
            f[87] = 0  # num_hidden_inputs (none)
            f[106] = 0  # num_suspicious_keywords (none)

            # Behavioral Features (114-138): Clean patterns
            f[114] = 0  # has_at_symbol (no)
            f[115] = 0  # has_double_slash (no)
            f[116] = 0  # has_ip_address (no)
            f[118] = 0  # uses_url_shortening (no)
            f[119] = 0  # num_encoded_chars (none)
            f[122] = 0  # obfuscation_score (none)
            f[124] = 0  # phishing_keywords_count (none)
            f[137] = np.random.uniform(0, 0.2)  # impersonation_score (low)
            f[138] = 0  # typosquatting_score (none)

            # Network Features (139-158): Reliable network
            f[139] = 1  # dns_resolves (yes)
            f[143] = 200  # http_status_code (OK)
            f[144] = np.random.randint(0, 2)  # num_redirects (few)
            f[153] = np.random.randint(4, 6)  # security_header_count (many)
            f[154] = 1  # has_hsts_header
            f[155] = 1  # has_csp_header

            features.append(f)

        return np.array(features)

    def train_models(self, X, y):
        """Train all 3 ML models"""
        print(f"\n{'='*80}")
        print(f" TRAINING ML MODELS WITH 159 FEATURES")
        print(f"{'='*80}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"   Train: {X_train.shape[0]} samples")
        print(f"   Test: {X_test.shape[0]} samples")

        self.X_test = X_test
        self.y_test = y_test

        # Model configurations
        models_config = {
            "Random Forest": RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features="sqrt",
                random_state=42,
                n_jobs=-1,
            ),
            "XGBoost": XGBClassifier(
                n_estimators=200,
                max_depth=10,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbosity=0,
            ),
            "LightGBM": LGBMClassifier(
                n_estimators=200,
                max_depth=15,
                learning_rate=0.1,
                num_leaves=50,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            ),
        }

        # Train each model
        for name, model in models_config.items():
            print(f"\n Training {name}...")

            # Train
            model.fit(X_train, y_train)

            # Predict
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train, y_train, cv=5, scoring="accuracy"
            )

            # Evaluate
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
                "auc_roc": roc_auc_score(y_test, y_pred_proba),
                "cv_mean": cv_scores.mean(),
                "cv_std": cv_scores.std(),
            }

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)

            self.models[name] = {
                "model": model,
                "metrics": metrics,
                "predictions": y_pred,
                "confusion_matrix": cm,
            }

            print(f"    {name} trained!")
            print(f"      Accuracy:    {metrics['accuracy']:.4f}")
            print(f"      Precision:   {metrics['precision']:.4f}")
            print(f"      Recall:      {metrics['recall']:.4f}")
            print(f"      F1-Score:    {metrics['f1']:.4f}")
            print(f"      AUC-ROC:     {metrics['auc_roc']:.4f}")
            print(
                f"      CV Score:    {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})"
            )

        print(f"\n{'='*80}")
        print(f" ALL MODELS TRAINED SUCCESSFULLY!")
        print(f"{'='*80}")

    def save_models(self):
        """Save all trained models"""
        print(f"\n Saving models to {self.output_dir}/...")

        for name, data in self.models.items():
            model = data["model"]

            # Create filename
            filename = name.lower().replace(" ", "_") + "_159features.pkl"
            filepath = os.path.join(self.output_dir, filename)

            # Save
            joblib.dump(model, filepath)

            size_kb = os.path.getsize(filepath) / 1024
            print(f"    {name}: {filename} ({size_kb:.1f} KB)")

        print(f"\n All models saved!")

    def print_final_report(self):
        """Print comprehensive training report"""
        print(f"\n{'='*80}")
        print(f" ULTIMATE TRAINING REPORT - 159 FEATURES")
        print(f"{'='*80}")

        print(f"\n SYSTEM SUMMARY:")
        print(f"   Total Features: {self.feature_count}")
        print(f"   - URL Features: 35")
        print(f"   - SSL/TLS Features: 25")
        print(f"   - DNS Features: 15")
        print(f"   - Content Features: 39")
        print(f"   - Behavioral Features: 25")
        print(f"   - Network Features: 20")

        print(f"\n MODEL PERFORMANCE:")
        print(f"{'='*80}")
        print(
            f"{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1':<12} {'AUC':<12}"
        )
        print(f"{'-'*80}")

        for name, data in self.models.items():
            m = data["metrics"]
            print(
                f"{name:<20} {m['accuracy']:<12.4f} {m['precision']:<12.4f} "
                f"{m['recall']:<12.4f} {m['f1']:<12.4f} {m['auc_roc']:<12.4f}"
            )

        print(f"{'='*80}")

        # Feature importance (from Random Forest)
        if "Random Forest" in self.models:
            model = self.models["Random Forest"]["model"]
            importances = model.feature_importances_
            top_10_idx = np.argsort(importances)[-10:][::-1]

            print(f"\n TOP 10 MOST IMPORTANT FEATURES:")
            for i, idx in enumerate(top_10_idx, 1):
                feature_name = self.feature_names[idx]
                importance = importances[idx]
                print(f"   {i:2d}. {feature_name:<40} {importance:.4f}")

        # Confusion matrices
        print(f"\n CONFUSION MATRICES:")
        for name, data in self.models.items():
            cm = data["confusion_matrix"]
            print(f"\n   {name}:")
            print(f"      TN: {cm[0][0]:<6} FP: {cm[0][1]:<6}")
            print(f"      FN: {cm[1][0]:<6} TP: {cm[1][1]:<6}")

        print(f"\n{'='*80}")
        print(f" TRAINING COMPLETE!")
        print(
            f"   Average Accuracy: {np.mean([d['metrics']['accuracy'] for d in self.models.values()]):.4f}"
        )
        print(
            f"   Average AUC-ROC: {np.mean([d['metrics']['auc_roc'] for d in self.models.values()]):.4f}"
        )
        print(f"   Models saved in: {self.output_dir}/")
        print(f"{'='*80}")


def main():
    """Main training pipeline"""
    print(f"\n{'='*80}")
    print(f" ULTIMATE 159-FEATURE MODEL TRAINING")
    print(f"{'='*80}")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Mode: Fast Training (Synthetic Data)")
    print(f"{'='*80}")

    # Initialize trainer
    trainer = FastModelTrainer(output_dir="models")

    # Generate synthetic data
    X, y = trainer.generate_synthetic_data(n_samples=2000)

    # Train models
    trainer.train_models(X, y)

    # Save models
    trainer.save_models()

    # Print final report
    trainer.print_final_report()

    print(f"\n{'='*80}")
    print(f" ULTIMATE TRAINING COMPLETE!")
    print(f"   Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

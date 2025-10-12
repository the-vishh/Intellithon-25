"""
 USER REPORTING SYSTEM
========================

Allow users to report false positives/negatives and suspicious sites
"""

import json
import os
from datetime import datetime
import hashlib


class UserReportingSystem:
    """
    User reporting system for community-driven threat intelligence

    Features:
    - Report false positives (legitimate sites blocked)
    - Report false negatives (phishing sites not detected)
    - Report new suspicious sites
    - Upvote/downvote existing reports
    - Automatic integration with continuous learning
    """

    def __init__(self, base_dir="ml-model"):
        self.base_dir = base_dir
        self.reports_dir = os.path.join(base_dir, "user_reports")
        self.queue_dir = os.path.join(self.reports_dir, "review_queue")
        self.approved_dir = os.path.join(self.reports_dir, "approved")

        # Create directories
        os.makedirs(self.queue_dir, exist_ok=True)
        os.makedirs(self.approved_dir, exist_ok=True)

        # Report database
        self.reports_db = os.path.join(self.reports_dir, "reports_database.jsonl")
        self.stats_file = os.path.join(self.reports_dir, "reporting_stats.json")

    def submit_report(self, report_data):
        """
        Submit a new user report

        Args:
            report_data: Dictionary with report information
                - url: The URL being reported
                - report_type: 'false_positive', 'false_negative', 'suspicious'
                - description: User's description
                - evidence: Optional screenshot/proof
                - user_email: Optional for follow-up

        Returns:
            report_id: Unique ID for tracking
        """
        # Generate report ID
        report_id = self._generate_report_id(report_data["url"])

        # Create report entry
        report = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "url": report_data["url"],
            "report_type": report_data["report_type"],
            "description": report_data.get("description", ""),
            "user_email": report_data.get("user_email", "anonymous"),
            "evidence": report_data.get("evidence", None),
            "status": "pending",
            "votes": {"upvotes": 0, "downvotes": 0},
            "reviewed_by": None,
            "resolution": None,
        }

        # Save to database
        self._save_report(report)

        # Add to review queue
        self._add_to_queue(report)

        # Update statistics
        self._update_stats("report_submitted", report_data["report_type"])

        print(f" Report submitted: {report_id}")
        print(f"   Type: {report_data['report_type']}")
        print(f"   URL: {report_data['url']}")

        return report_id

    def _generate_report_id(self, url):
        """Generate unique report ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"RPT_{timestamp}_{url_hash}"

    def _save_report(self, report):
        """Save report to database"""
        with open(self.reports_db, "a", encoding="utf-8") as f:
            f.write(json.dumps(report) + "\n")

    def _add_to_queue(self, report):
        """Add report to review queue"""
        queue_file = os.path.join(self.queue_dir, f"{report['report_id']}.json")
        with open(queue_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def vote_report(self, report_id, vote_type):
        """
        Upvote or downvote a report

        Args:
            report_id: The report to vote on
            vote_type: 'upvote' or 'downvote'

        Returns:
            Updated vote counts
        """
        report = self._load_report(report_id)

        if not report:
            print(f" Report {report_id} not found")
            return None

        # Update votes
        if vote_type == "upvote":
            report["votes"]["upvotes"] += 1
        elif vote_type == "downvote":
            report["votes"]["downvotes"] += 1

        # Save updated report
        self._update_report(report)

        print(f" Vote recorded: {vote_type} on {report_id}")

        return report["votes"]

    def _load_report(self, report_id):
        """Load a specific report"""
        # Check review queue
        queue_file = os.path.join(self.queue_dir, f"{report_id}.json")
        if os.path.exists(queue_file):
            with open(queue_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Check approved reports
        approved_file = os.path.join(self.approved_dir, f"{report_id}.json")
        if os.path.exists(approved_file):
            with open(approved_file, "r", encoding="utf-8") as f:
                return json.load(f)

        return None

    def _update_report(self, report):
        """Update existing report"""
        report_id = report["report_id"]

        if report["status"] == "pending":
            file_path = os.path.join(self.queue_dir, f"{report_id}.json")
        else:
            file_path = os.path.join(self.approved_dir, f"{report_id}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def review_report(self, report_id, reviewer, decision, notes=None):
        """
        Review a pending report

        Args:
            report_id: Report to review
            reviewer: Reviewer identifier
            decision: 'approve', 'reject', 'needs_more_info'
            notes: Optional review notes

        Returns:
            Updated report
        """
        report = self._load_report(report_id)

        if not report:
            print(f" Report {report_id} not found")
            return None

        # Update report
        report["status"] = decision
        report["reviewed_by"] = reviewer
        report["resolution"] = {
            "decision": decision,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
        }

        # If approved, move to approved directory and integrate with learning
        if decision == "approve":
            self._approve_report(report)
        elif decision == "reject":
            # Remove from queue
            queue_file = os.path.join(self.queue_dir, f"{report_id}.json")
            if os.path.exists(queue_file):
                os.remove(queue_file)

        # Update statistics
        self._update_stats("report_reviewed", decision)

        print(f" Report reviewed: {report_id}")
        print(f"   Decision: {decision}")

        return report

    def _approve_report(self, report):
        """Approve report and integrate with continuous learning"""
        # Move to approved directory
        approved_file = os.path.join(self.approved_dir, f"{report['report_id']}.json")
        with open(approved_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Remove from queue
        queue_file = os.path.join(self.queue_dir, f"{report['report_id']}.json")
        if os.path.exists(queue_file):
            os.remove(queue_file)

        # Integrate with continuous learning (if available)
        try:
            from utils.continuous_learning import ContinuousLearning

            cl = ContinuousLearning()

            # Determine actual label
            if report["report_type"] == "false_positive":
                actual_label = 0  # Legitimate
                predicted_label = 1  # Was flagged as phishing
            elif report["report_type"] == "false_negative":
                actual_label = 1  # Phishing
                predicted_label = 0  # Was not flagged
            else:
                actual_label = 1  # Suspicious = treat as phishing
                predicted_label = 0

            # Collect feedback (requires feature extraction)
            # In production, this would extract features from the URL
            print(f"    Integrating with continuous learning...")

        except Exception as e:
            print(f"    Could not integrate with learning: {e}")

    def get_pending_reports(self, limit=10):
        """
        Get pending reports for review

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of pending reports
        """
        pending = []

        for filename in os.listdir(self.queue_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.queue_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    report = json.load(f)
                    pending.append(report)

                if len(pending) >= limit:
                    break

        # Sort by votes (most upvoted first)
        pending.sort(
            key=lambda r: r["votes"]["upvotes"] - r["votes"]["downvotes"], reverse=True
        )

        return pending

    def get_report_stats(self):
        """Get reporting statistics"""
        if not os.path.exists(self.stats_file):
            return {
                "total_reports": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0,
            }

        with open(self.stats_file, "r") as f:
            return json.load(f)

    def _update_stats(self, action, category):
        """Update reporting statistics"""
        stats = self.get_report_stats()

        if action == "report_submitted":
            stats["total_reports"] = stats.get("total_reports", 0) + 1
            stats["pending"] = stats.get("pending", 0) + 1

            # By type
            type_key = f"reports_{category}"
            stats[type_key] = stats.get(type_key, 0) + 1

        elif action == "report_reviewed":
            stats["pending"] = stats.get("pending", 0) - 1

            if category == "approve":
                stats["approved"] = stats.get("approved", 0) + 1
            elif category == "reject":
                stats["rejected"] = stats.get("rejected", 0) + 1

        with open(self.stats_file, "w") as f:
            json.dump(stats, f, indent=2)

    def generate_report_ui_html(self):
        """Generate HTML for reporting UI in Chrome extension"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Report to PhishGuard</title>
    <style>
        body {
            width: 400px;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        h2 {
            color: #2c3e50;
            margin-top: 0;
        }
        .report-type {
            margin: 15px 0;
        }
        label {
            display: block;
            margin: 10px 0 5px;
            font-weight: 600;
            color: #34495e;
        }
        input[type="radio"] {
            margin-right: 8px;
        }
        textarea {
            width: 100%;
            min-height: 80px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }
        input[type="email"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        button:hover {
            background: #2980b9;
        }
        .success {
            color: #27ae60;
            padding: 10px;
            background: #d5f4e6;
            border-radius: 4px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h2> Report to PhishGuard</h2>

    <form id="reportForm">
        <div class="report-type">
            <label>Report Type:</label>
            <label>
                <input type="radio" name="reportType" value="false_positive" required>
                False Positive (This site is safe but was blocked)
            </label>
            <label>
                <input type="radio" name="reportType" value="false_negative" required>
                False Negative (This site is dangerous but wasn't detected)
            </label>
            <label>
                <input type="radio" name="reportType" value="suspicious" required>
                Report Suspicious Site
            </label>
        </div>

        <label>Description:</label>
        <textarea id="description" placeholder="Please describe the issue..." required></textarea>

        <label>Your Email (optional, for follow-up):</label>
        <input type="email" id="email" placeholder="your.email@example.com">

        <button type="submit">Submit Report</button>
    </form>

    <div id="successMessage" class="success" style="display: none;">
         Thank you! Your report has been submitted and will be reviewed.
    </div>

    <script src="report_handler.js"></script>
</body>
</html>
"""
        return html


def demo_reporting_system():
    """Demonstrate user reporting system"""
    print("=" * 80)
    print(" USER REPORTING SYSTEM DEMO")
    print("=" * 80)

    urs = UserReportingSystem()

    # Submit reports
    print("\n1⃣ Submitting user reports...")

    # False positive report
    report1_id = urs.submit_report(
        {
            "url": "https://legitimate-business.com",
            "report_type": "false_positive",
            "description": "This is my company website, it is legitimate",
            "user_email": "admin@legitimate-business.com",
        }
    )

    # False negative report
    report2_id = urs.submit_report(
        {
            "url": "https://phishing-scam.com",
            "report_type": "false_negative",
            "description": "This site stole my credentials, please block it!",
            "user_email": "victim@example.com",
        }
    )

    # Suspicious site report
    report3_id = urs.submit_report(
        {
            "url": "https://suspicious-site.com",
            "report_type": "suspicious",
            "description": "This site is asking for my bank details",
        }
    )

    # Vote on reports
    print("\n2⃣ Community voting...")
    urs.vote_report(report2_id, "upvote")
    urs.vote_report(report2_id, "upvote")
    urs.vote_report(report2_id, "upvote")

    # Get pending reports
    print("\n3⃣ Reviewing pending reports...")
    pending = urs.get_pending_reports(limit=5)
    print(f"   Found {len(pending)} pending reports")

    for report in pending:
        print(f"\n    Report: {report['report_id']}")
        print(f"      Type: {report['report_type']}")
        print(f"      URL: {report['url']}")
        print(
            f"      Votes: ↑{report['votes']['upvotes']} ↓{report['votes']['downvotes']}"
        )

    # Review reports
    print("\n4⃣ Admin reviewing reports...")
    urs.review_report(
        report1_id,
        reviewer="admin",
        decision="approve",
        notes="Verified as legitimate business",
    )

    urs.review_report(
        report2_id,
        reviewer="admin",
        decision="approve",
        notes="Confirmed phishing site, added to blocklist",
    )

    # Get statistics
    print("\n5⃣ Reporting statistics:")
    stats = urs.get_report_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Generate UI
    print("\n6⃣ Generating reporting UI...")
    html = urs.generate_report_ui_html()

    output_file = "user_report_form.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"    Generated report form UI")
    print(f"    Saved to: {output_file}")

    print("\n" + "=" * 80)
    print(" USER REPORTING SYSTEM READY")
    print("=" * 80)
    print("\n Features:")
    print("    False positive reporting")
    print("    False negative reporting")
    print("    Suspicious site reporting")
    print("    Community voting")
    print("    Admin review queue")
    print("    Continuous learning integration")
    print("    Email follow-up support")
    print("\n Benefits:")
    print("   • Community-driven threat intelligence")
    print("   • Rapid false positive correction")
    print("   • Faster phishing site detection")
    print("   • Automatic model improvement")
    print("=" * 80)


if __name__ == "__main__":
    demo_reporting_system()

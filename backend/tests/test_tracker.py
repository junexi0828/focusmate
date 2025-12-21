"""
Test Tracking and Reporting System
테스트 추적 및 보고 시스템
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class TestTracker:
    """Test execution tracker for monitoring and reporting."""

    def __init__(self, output_dir: str = "test_reports"):
        """Initialize test tracker.

        Args:
            output_dir: Directory to save test reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "categories": {
                "unit": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "integration": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "e2e": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "performance": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "security": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
            },
            "test_details": [],
            "summary": {}
        }

    def record_test(self, category: str, test_name: str, status: str,
                   duration: float = 0.0, error: str = None):
        """Record a test result.

        Args:
            category: Test category (unit, integration, e2e, performance, security)
            test_name: Name of the test
            status: Test status (passed, failed, skipped)
            duration: Test duration in seconds
            error: Error message if failed
        """
        if category not in self.results["categories"]:
            category = "unit"  # Default

        self.results["categories"][category]["total"] += 1
        self.results["categories"][category][status] += 1

        self.results["test_details"].append({
            "category": category,
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_summary(self):
        """Calculate test summary statistics."""
        total = sum(cat["total"] for cat in self.results["categories"].values())
        passed = sum(cat["passed"] for cat in self.results["categories"].values())
        failed = sum(cat["failed"] for cat in self.results["categories"].values())
        skipped = sum(cat["skipped"] for cat in self.results["categories"].values())

        self.results["summary"] = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "categories": len([c for c in self.results["categories"].values() if c["total"] > 0])
        }

    def save_report(self, filename: str = None):
        """Save test report to JSON file.

        Args:
            filename: Optional custom filename
        """
        self.calculate_summary()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return filepath

    def generate_markdown_report(self, filename: str = None):
        """Generate markdown test report.

        Args:
            filename: Optional custom filename
        """
        self.calculate_summary()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.md"

        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# FocusMate Test Report\n\n")
            f.write(f"**Generated**: {self.results['timestamp']}\n\n")

            # Summary
            summary = self.results["summary"]
            f.write("## Summary\n\n")
            f.write(f"- **Total Tests**: {summary['total']}\n")
            f.write(f"- **Passed**: {summary['passed']} ({summary['pass_rate']:.1f}%)\n")
            f.write(f"- **Failed**: {summary['failed']}\n")
            f.write(f"- **Skipped**: {summary['skipped']}\n")
            f.write(f"- **Categories**: {summary['categories']}\n\n")

            # Category breakdown
            f.write("## Category Breakdown\n\n")
            f.write("| Category | Total | Passed | Failed | Skipped | Pass Rate |\n")
            f.write("|----------|-------|--------|--------|---------|-----------|\n")

            for cat_name, cat_data in self.results["categories"].items():
                if cat_data["total"] > 0:
                    pass_rate = (cat_data["passed"] / cat_data["total"] * 100) if cat_data["total"] > 0 else 0
                    f.write(f"| {cat_name} | {cat_data['total']} | {cat_data['passed']} | "
                           f"{cat_data['failed']} | {cat_data['skipped']} | {pass_rate:.1f}% |\n")

            # Failed tests
            failed_tests = [t for t in self.results["test_details"] if t["status"] == "failed"]
            if failed_tests:
                f.write("\n## Failed Tests\n\n")
                for test in failed_tests:
                    f.write(f"### {test['test_name']}\n\n")
                    f.write(f"- **Category**: {test['category']}\n")
                    f.write(f"- **Duration**: {test['duration']:.3f}s\n")
                    if test["error"]:
                        f.write(f"- **Error**: {test['error']}\n")
                    f.write("\n")

        return filepath

    def load_report(self, filename: str) -> dict[str, Any]:
        """Load a test report from file.

        Args:
            filename: Report filename

        Returns:
            Test results dictionary
        """
        filepath = self.output_dir / filename
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)


# Global tracker instance
_tracker = None


def get_tracker() -> TestTracker:
    """Get global test tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = TestTracker()
    return _tracker


"""
FocusMate Test Suite
모듈화된 테스트 시스템
"""

__version__ = "1.0.0"

# Test categories
TEST_CATEGORIES = {
    "unit": "단위 테스트",
    "integration": "통합 테스트",
    "e2e": "E2E 테스트",
    "performance": "성능 테스트",
    "security": "보안 테스트"
}

# Test tracking
TEST_TRACKER = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "skipped_tests": 0,
    "categories": {}
}


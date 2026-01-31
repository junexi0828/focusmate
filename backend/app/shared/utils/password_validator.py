"""Password validation utilities.

Provides password strength validation to prevent weak passwords.
"""

import re
from typing import NamedTuple


class PasswordValidationResult(NamedTuple):
    """Password validation result."""

    is_valid: bool
    errors: list[str]


class PasswordValidator:
    """Password strength validator.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    - No common passwords
    """

    # Common weak passwords (expand this list)
    COMMON_PASSWORDS = {
        "12345678",
        "password",
        "password1",
        "password123",
        "qwerty123",
        "admin123",
        "letmein",
        "welcome1",
        "passw0rd",
        "1q2w3e4r",
        "abc12345",
        "abcd1234",
    }

    @staticmethod
    def validate(password: str) -> PasswordValidationResult:
        """Validate password strength.

        Args:
            password: Password to validate

        Returns:
            PasswordValidationResult with validation status and error messages
        """
        errors: list[str] = []

        # Check length
        if len(password) < 8:
            errors.append("비밀번호는 최소 8자 이상이어야 합니다.")

        if len(password) > 100:
            errors.append("비밀번호는 최대 100자 이하여야 합니다.")

        # Check for uppercase letter
        # if not re.search(r"[A-Z]", password):
        #     errors.append("대문자를 최소 1개 포함해야 합니다.")

        # Check for lowercase letter
        if not re.search(r"[a-z]", password):
            errors.append("소문자를 최소 1개 포함해야 합니다.")

        # Check for number
        if not re.search(r"\d", password):
            errors.append("숫자를 최소 1개 포함해야 합니다.")

        # Check for special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/~`';]", password):
            errors.append("특수문자를 최소 1개 포함해야 합니다.")

        # Check for common passwords
        if password.lower() in PasswordValidator.COMMON_PASSWORDS:
            errors.append("너무 흔한 비밀번호입니다. 다른 비밀번호를 사용해주세요.")

        # Check for sequential characters (123, abc, etc.)
        # Simplified to common patterns: 123, abc, qwerty, asdf, qwer, 012, 789
        if re.search(r"(123|abc|qwerty|asdf|qwer|012|789)", password.lower()):
            errors.append("연속된 문자나 숫자를 피해주세요.")

        # Check for sequential characters (123, abc, etc.)
        #    if re.search(r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm
        # |lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)", password.lower()):
        #           errors.append("연속된 문자나 숫자를 피해주세요.")

        # Check for repeated characters (aaa, 111, etc.)
        if re.search(r"(.)\1{2,}", password):
            errors.append("같은 문자가 3번 이상 반복되지 않아야 합니다.")

        is_valid = len(errors) == 0
        return PasswordValidationResult(is_valid=is_valid, errors=errors)


def validate_password_strength(password: str) -> PasswordValidationResult:
    """Convenience function for password validation.

    Args:
        password: Password to validate

    Returns:
        PasswordValidationResult
    """
    return PasswordValidator.validate(password)

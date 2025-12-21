"""Encryption utilities for sensitive data.

Uses Fernet (symmetric encryption) for file and data encryption.
Fernet is built on top of AES 128 in CBC mode with HMAC authentication.
"""

import base64
import binascii

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""

    def __init__(self, encryption_key: str | None = None) -> None:
        """Initialize encryption service.

        Args:
            encryption_key: Base64-encoded Fernet key. If None, derives from SECRET_KEY.
        """
        if encryption_key:
            # Use provided key (must be base64-encoded Fernet key)
            if isinstance(encryption_key, str):
                self.key = encryption_key.encode()
            else:
                self.key = encryption_key
        else:
            # Derive key from SECRET_KEY (deterministic, no token generation needed)
            self.key = self._derive_key_from_secret(settings.SECRET_KEY)

        self.cipher = Fernet(self.key)

    @staticmethod
    def _derive_key_from_secret(secret: str) -> bytes:
        """Derive a Fernet key from a secret string.

        This allows using SECRET_KEY without generating/storing a separate key.
        Uses PBKDF2 with SHA256 to derive a 32-byte key.

        Args:
            secret: Secret string (e.g., SECRET_KEY)

        Returns:
            Base64-encoded Fernet key
        """
        # Use a fixed salt (can be stored in config if needed)
        salt = b"focus_mate_verification_salt"  # Fixed salt for deterministic key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Standard PBKDF2 iterations
        )
        return base64.urlsafe_b64encode(kdf.derive(secret.encode()))

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data.

        Args:
            data: Raw data to encrypt

        Returns:
            Encrypted data
        """
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted data

        Raises:
            ValueError: If decryption fails (invalid token)
        """
        try:
            return self.cipher.decrypt(encrypted_data)
        except InvalidToken as e:
            error_msg = "Failed to decrypt data: invalid token"
            raise ValueError(error_msg) from e

    def encrypt_string(self, text: str) -> str:
        """Encrypt a string and return base64-encoded result.

        Args:
            text: Plain text string

        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.encrypt(text.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt a base64-encoded encrypted string.

        Args:
            encrypted_text: Base64-encoded encrypted string

        Returns:
            Decrypted plain text string

        Raises:
            ValueError: If decryption fails
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode("utf-8"))
            decrypted = self.decrypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except (ValueError, binascii.Error) as e:
            error_msg = f"Failed to decrypt string: {e}"
            raise ValueError(error_msg) from e


# Global encryption service instance
_encryption_service: EncryptionService | None = None


def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        # Use FILE_ENCRYPTION_KEY from settings if available, otherwise derive from SECRET_KEY
        encryption_key = getattr(settings, "FILE_ENCRYPTION_KEY", None)
        _encryption_service = EncryptionService(encryption_key=encryption_key)
    return _encryption_service


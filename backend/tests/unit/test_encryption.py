"""Unit tests for encryption service.

Tests the Fernet-based encryption/decryption functionality.
"""

import pytest

from app.shared.utils.encryption import EncryptionService, get_encryption_service


class TestEncryptionService:
    """Test suite for EncryptionService."""

    def test_encrypt_decrypt_bytes(self):
        """Test encryption and decryption of binary data."""
        service = get_encryption_service()

        original_data = b"sensitive binary data"

        # Encrypt
        encrypted_data = service.encrypt(original_data)

        # Encrypted should be different from original
        assert encrypted_data != original_data

        # Decrypt
        decrypted_data = service.decrypt(encrypted_data)

        # Should match original
        assert decrypted_data == original_data

    def test_encrypt_decrypt_string(self):
        """Test encryption and decryption of string data."""
        service = get_encryption_service()

        original_text = "sensitive text data"

        # Encrypt
        encrypted_text = service.encrypt_string(original_text)

        # Encrypted should be different and base64 encoded
        assert encrypted_text != original_text
        assert isinstance(encrypted_text, str)

        # Decrypt
        decrypted_text = service.decrypt_string(encrypted_text)

        # Should match original
        assert decrypted_text == original_text

    def test_encryption_is_non_deterministic(self):
        """Test that encrypting the same data twice produces different ciphertext."""
        service = get_encryption_service()

        original_data = b"same data"

        # Encrypt twice
        encrypted1 = service.encrypt(original_data)
        encrypted2 = service.encrypt(original_data)

        # Different ciphertext (due to IV/nonce)
        assert encrypted1 != encrypted2

        # But both should decrypt to same original
        assert service.decrypt(encrypted1) == original_data
        assert service.decrypt(encrypted2) == original_data

    def test_decrypt_invalid_token_raises_error(self):
        """Test that decrypting invalid data raises ValueError."""
        service = get_encryption_service()

        invalid_encrypted_data = b"invalid encrypted data"

        with pytest.raises(ValueError, match="Failed to decrypt"):
            service.decrypt(invalid_encrypted_data)

    def test_decrypt_string_invalid_data_raises_error(self):
        """Test that decrypting invalid string raises ValueError."""
        service = get_encryption_service()

        invalid_encrypted_text = "not a valid encrypted string"

        with pytest.raises(ValueError, match="Failed to decrypt"):
            service.decrypt_string(invalid_encrypted_text)

    def test_empty_data_encryption(self):
        """Test encryption of empty data."""
        service = get_encryption_service()

        # Empty bytes
        encrypted = service.encrypt(b"")
        decrypted = service.decrypt(encrypted)
        assert decrypted == b""

        # Empty string
        encrypted_str = service.encrypt_string("")
        decrypted_str = service.decrypt_string(encrypted_str)
        assert decrypted_str == ""

    def test_large_data_encryption(self):
        """Test encryption of large data."""
        service = get_encryption_service()

        # Generate 1MB of data
        large_data = b"x" * (1024 * 1024)

        encrypted = service.encrypt(large_data)
        decrypted = service.decrypt(encrypted)

        assert decrypted == large_data

    def test_unicode_string_encryption(self):
        """Test encryption of unicode strings."""
        service = get_encryption_service()

        unicode_text = "안녕하세요 🔒 こんにちは"

        encrypted = service.encrypt_string(unicode_text)
        decrypted = service.decrypt_string(encrypted)

        assert decrypted == unicode_text

    def test_key_derivation_from_secret(self):
        """Test that key derivation is deterministic."""
        secret = "test_secret_key"

        service1 = EncryptionService(encryption_key=None)
        service2 = EncryptionService(encryption_key=None)

        # Same secret should produce same key
        assert service1.key == service2.key

    def test_custom_encryption_key(self):
        """Test using a custom encryption key."""
        from cryptography.fernet import Fernet

        # Generate a custom key
        custom_key = Fernet.generate_key()

        # Create service with custom key
        service = EncryptionService(encryption_key=custom_key.decode())

        original_data = b"test data"
        encrypted = service.encrypt(original_data)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original_data

    def test_get_encryption_service_singleton(self):
        """Test that get_encryption_service returns singleton."""
        service1 = get_encryption_service()
        service2 = get_encryption_service()

        # Should be same instance
        assert service1 is service2

    def test_binary_file_simulation(self):
        """Test encryption/decryption simulating file operations."""
        service = get_encryption_service()

        # Simulate reading a file
        file_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00"

        # Encrypt (simulating upload)
        encrypted_content = service.encrypt(file_content)

        # Decrypt (simulating download)
        decrypted_content = service.decrypt(encrypted_content)

        assert decrypted_content == file_content

    def test_encryption_preserves_data_integrity(self):
        """Test that encryption/decryption preserves exact data."""
        service = get_encryption_service()

        test_cases = [
            b"simple text",
            b"\x00\x01\x02\x03",  # Binary with null bytes
            b"line1\nline2\rline3",  # Newlines
            b"\t\t\ttabs",  # Tabs
            "한글 unicode".encode("utf-8"),  # UTF-8 encoded
        ]

        for original in test_cases:
            encrypted = service.encrypt(original)
            decrypted = service.decrypt(encrypted)
            assert decrypted == original, f"Failed for {original!r}"

    @pytest.mark.benchmark
    def test_encryption_performance(self, benchmark):
        """Benchmark encryption performance (optional test)."""
        service = get_encryption_service()
        data = b"benchmark data" * 100

        # Benchmark encryption
        result = benchmark(service.encrypt, data)
        assert len(result) > 0

    @pytest.mark.benchmark
    def test_decryption_performance(self, benchmark):
        """Benchmark decryption performance (optional test)."""
        service = get_encryption_service()
        data = b"benchmark data" * 100
        encrypted = service.encrypt(data)

        # Benchmark decryption
        result = benchmark(service.decrypt, encrypted)
        assert result == data

"""Unit tests for encrypted file upload service.

Tests file upload with encryption functionality.
"""

import os
import tempfile
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.infrastructure.storage.encrypted_file_upload import (
    EncryptedFileUploadService,
)
from app.shared.utils.encryption import get_encryption_service


@pytest.fixture
def upload_service():
    """Create encrypted file upload service."""
    return EncryptedFileUploadService()


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestEncryptedFileUploadService:
    """Test suite for EncryptedFileUploadService."""

    @pytest.mark.asyncio
    async def test_upload_file_encrypts_content(self, upload_service, temp_upload_dir):
        """Test that uploaded file is encrypted."""
        # Create mock upload file
        file_content = b"test file content"
        file = UploadFile(
            filename="test.txt",
            file=BytesIO(file_content),
        )

        # Upload file
        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".txt"],
        )

        # Read stored file
        full_path = Path(file_path)
        assert full_path.exists()

        with open(full_path, "rb") as f:
            stored_content = f.read()

        # Stored content should be different (encrypted)
        assert stored_content != file_content

        # Cleanup
        os.remove(full_path)

    @pytest.mark.asyncio
    async def test_download_file_decrypts_content(self, upload_service, temp_upload_dir):
        """Test that downloaded file is decrypted."""
        # Create mock upload file
        file_content = b"secret file content"
        file = UploadFile(
            filename="secret.txt",
            file=BytesIO(file_content),
        )

        # Upload file (encrypts)
        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".txt"],
        )

        # Download file (decrypts)
        decrypted_content = await upload_service.download_encrypted_file(file_path)

        # Should match original
        assert decrypted_content == file_content

        # Cleanup
        os.remove(file_path)

    @pytest.mark.asyncio
    async def test_upload_download_roundtrip(self, upload_service, temp_upload_dir):
        """Test complete upload-download cycle."""
        # Test with various file types
        test_cases = [
            ("text.txt", b"plain text content"),
            ("image.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF"),  # JPEG header
            ("document.pdf", b"%PDF-1.4\n"),  # PDF header
            ("unicode.txt", "한글 내용 🔒".encode("utf-8")),
        ]

        for filename, content in test_cases:
            file = UploadFile(
                filename=filename,
                file=BytesIO(content),
            )

            # Upload
            file_path = await upload_service.upload_file(
                file=file,
                folder=temp_upload_dir,
                allowed_extensions=[".txt", ".jpg", ".pdf"],
            )

            # Download
            decrypted = await upload_service.download_encrypted_file(file_path)

            # Verify
            assert decrypted == content, f"Failed for {filename}"

            # Cleanup
            os.remove(file_path)

    @pytest.mark.asyncio
    async def test_file_extension_validation(self, upload_service, temp_upload_dir):
        """Test that file extension is validated."""
        # Try to upload file with disallowed extension
        file = UploadFile(
            filename="malicious.exe",
            file=BytesIO(b"malicious content"),
        )

        with pytest.raises(ValueError, match="File type not allowed"):
            await upload_service.upload_file(
                file=file,
                folder=temp_upload_dir,
                allowed_extensions=[".txt", ".jpg"],
            )

    @pytest.mark.asyncio
    async def test_delete_encrypted_file(self, upload_service, temp_upload_dir):
        """Test file deletion."""
        # Upload file
        file_content = b"to be deleted"
        file = UploadFile(
            filename="delete.txt",
            file=BytesIO(file_content),
        )

        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".txt"],
        )

        assert Path(file_path).exists()

        # Delete file
        success = await upload_service.delete_file(file_path)
        assert success is True
        assert not Path(file_path).exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(self, upload_service):
        """Test deleting non-existent file returns False."""
        success = await upload_service.delete_file("/nonexistent/path/file.txt")
        assert success is False

    @pytest.mark.asyncio
    async def test_large_file_encryption(self, upload_service, temp_upload_dir):
        """Test encryption of large files."""
        # Create 5MB file
        large_content = b"x" * (5 * 1024 * 1024)

        file = UploadFile(
            filename="large.bin",
            file=BytesIO(large_content),
        )

        # Upload
        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".bin"],
        )

        # Download and verify
        decrypted = await upload_service.download_encrypted_file(file_path)
        assert decrypted == large_content

        # Cleanup
        os.remove(file_path)

    @pytest.mark.asyncio
    async def test_empty_file_handling(self, upload_service, temp_upload_dir):
        """Test handling of empty files."""
        file = UploadFile(
            filename="empty.txt",
            file=BytesIO(b""),
        )

        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".txt"],
        )

        decrypted = await upload_service.download_encrypted_file(file_path)
        assert decrypted == b""

        # Cleanup
        os.remove(file_path)

    @pytest.mark.asyncio
    async def test_filename_sanitization(self, upload_service, temp_upload_dir):
        """Test that filenames are sanitized."""
        # Filename with special characters
        file = UploadFile(
            filename="../../../etc/passwd.txt",
            file=BytesIO(b"content"),
        )

        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".txt"],
        )

        # Should not create file outside temp directory
        assert temp_upload_dir in file_path
        assert "../" not in file_path

        # Cleanup
        if Path(file_path).exists():
            os.remove(file_path)

    @pytest.mark.asyncio
    async def test_concurrent_uploads(self, upload_service, temp_upload_dir):
        """Test concurrent file uploads."""
        import asyncio

        async def upload_file(i: int):
            content = f"file {i} content".encode()
            file = UploadFile(
                filename=f"file_{i}.txt",
                file=BytesIO(content),
            )
            return await upload_service.upload_file(
                file=file,
                folder=temp_upload_dir,
                allowed_extensions=[".txt"],
            )

        # Upload 10 files concurrently
        file_paths = await asyncio.gather(*[upload_file(i) for i in range(10)])

        # Verify all files were created
        assert len(file_paths) == 10
        assert len(set(file_paths)) == 10  # All unique

        # Cleanup
        for path in file_paths:
            if Path(path).exists():
                os.remove(path)

    def test_encryption_service_integration(self, upload_service):
        """Test that service uses encryption service correctly."""
        encryption_service = get_encryption_service()

        # Test data
        data = b"integration test"

        # Encrypt using service
        encrypted = upload_service.encryption_service.encrypt(data)

        # Should be able to decrypt with encryption service
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == data

    @pytest.mark.asyncio
    async def test_file_metadata_preservation(self, upload_service, temp_upload_dir):
        """Test that file metadata can be preserved."""
        # Upload file
        file_content = b"metadata test"
        original_filename = "original_name.txt"

        file = UploadFile(
            filename=original_filename,
            file=BytesIO(file_content),
        )

        file_path = await upload_service.upload_file(
            file=file,
            folder=temp_upload_dir,
            allowed_extensions=[".txt"],
        )

        # Verify file exists
        assert Path(file_path).exists()

        # Cleanup
        os.remove(file_path)

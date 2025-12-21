"""Unit tests for encrypted file upload service."""

import tempfile
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.infrastructure.storage.encrypted_file_upload import (
    EncryptedFileUploadService,
)


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def upload_service(temp_upload_dir):
    """Create encrypted file upload service."""
    # Point upload_dir to temp dir for tests
    return EncryptedFileUploadService(upload_dir=temp_upload_dir)

class TestEncryptedFileUploadService:
    """Test suite for EncryptedFileUploadService."""

    @pytest.mark.asyncio
    async def test_save_file_encrypts_content(self, upload_service, temp_upload_dir):
        """Test that saved file is encrypted."""
        user_id = "user123"
        file_content = b"test file content"
        file = UploadFile(
            filename="test.pdf",
            file=BytesIO(file_content),
            size=len(file_content)
        )

        # Save file
        rel_path = await upload_service.save_file(file, user_id)

        # Verify file exists
        full_path = Path(temp_upload_dir).parent / rel_path
        assert full_path.exists()
        assert rel_path.endswith(".encrypted")

        # Read stored file
        with open(full_path, "rb") as f:
            stored_content = f.read()

        # Stored content should be different (encrypted)
        assert stored_content != file_content

        # Verify we can read it back
        decrypted = await upload_service.read_file(rel_path)
        assert decrypted == file_content

    @pytest.mark.asyncio
    async def test_read_file_decrypts_content(self, upload_service, temp_upload_dir):
        """Test that read file is decrypted."""
        user_id = "user456"
        file_content = b"secret file content"
        file = UploadFile(
            filename="secret.png",
            file=BytesIO(file_content),
            size=len(file_content)
        )

        # Save file (encrypts)
        rel_path = await upload_service.save_file(file, user_id)

        # Read file (decrypts by default)
        decrypted_content = await upload_service.read_file(rel_path)

        # Should match original
        assert decrypted_content == file_content

    @pytest.mark.asyncio
    async def test_file_extension_validation(self, upload_service):
        """Test that file extension is validated."""
        file = UploadFile(
            filename="malicious.exe",
            file=BytesIO(b"malicious content"),
            size=17
        )

        with pytest.raises(ValueError, match="Invalid file type"):
            await upload_service.save_file(file, "user1")

    @pytest.mark.asyncio
    async def test_delete_encrypted_file(self, upload_service, temp_upload_dir):
        """Test file deletion."""
        user_id = "user789"
        file = UploadFile(
            filename="delete.jpg",
            file=BytesIO(b"to be deleted"),
            size=13
        )

        rel_path = await upload_service.save_file(file, user_id)
        full_path = Path(temp_upload_dir).parent / rel_path
        assert full_path.exists()

        # Delete file
        success = upload_service.delete_file(rel_path)
        assert success is True
        assert not full_path.exists()

    @pytest.mark.asyncio
    async def test_large_file_encryption(self, upload_service, temp_upload_dir):
        """Test encryption of larger files."""
        user_id = "user_large"
        # 1MB file
        large_content = b"x" * (1024 * 1024)

        file = UploadFile(
            filename="large.pdf",
            file=BytesIO(large_content),
            size=len(large_content)
        )

        # Save
        rel_path = await upload_service.save_file(file, user_id)

        # Read and verify
        decrypted = await upload_service.read_file(rel_path)
        assert decrypted == large_content

    @pytest.mark.asyncio
    async def test_empty_file_handling(self, upload_service):
        """Test handling of empty files."""
        user_id = "user_empty"
        file = UploadFile(
            filename="empty.png",
            file=BytesIO(b""),
            size=0
        )

        rel_path = await upload_service.save_file(file, user_id)
        decrypted = await upload_service.read_file(rel_path)
        assert decrypted == b""

    @pytest.mark.asyncio
    async def test_save_multiple_files(self, upload_service):
        """Test saving multiple files."""
        user_id = "user_multi"
        files = [
            UploadFile(filename="f1.jpg", file=BytesIO(b"c1"), size=2),
            UploadFile(filename="f2.png", file=BytesIO(b"c2"), size=2),
        ]

        paths = await upload_service.save_multiple_files(files, user_id)
        assert len(paths) == 2

        for i, path in enumerate(paths):
            decrypted = await upload_service.read_file(path)
            assert decrypted == f"c{i+1}".encode()

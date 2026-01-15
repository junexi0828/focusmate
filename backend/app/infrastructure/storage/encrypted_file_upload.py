"""Encrypted file upload service for verification documents."""

import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.infrastructure.storage.file_upload import FileUploadService
from app.shared.utils.encryption import get_encryption_service

class EncryptedFileUploadService(FileUploadService):
    """File upload service with encryption support."""

    def __init__(self, upload_dir: str = "uploads/verification", encrypt: bool = True):
        """Initialize encrypted file upload service.

        Args:
            upload_dir: Directory to store uploaded files
            encrypt: Whether to encrypt files (default: True)
        """
        super().__init__(upload_dir)
        self.encrypt = encrypt
        # Always initialize encryption service (needed for decryption even if encrypt=False)
        self.encryption_service = get_encryption_service()

    async def save_file(self, file: UploadFile, user_id: str) -> str:
        """Save uploaded file with optional encryption.

        Args:
            file: Uploaded file
            user_id: User identifier

        Returns:
            Relative file path
        """
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)

        # Generate unique filename
        file_ext = Path(file.filename or "upload").suffix.lower()
        safe_user_id = self._safe_dir_name(user_id)
        unique_filename = f"{safe_user_id}_{uuid.uuid4().hex}{file_ext}"

        # Create user directory
        user_dir = self.upload_dir / safe_user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        # Read file content
        content = await self._read_with_limit(file)

        # Encrypt if enabled
        if self.encrypt and self.encryption_service:
            content = self.encryption_service.encrypt(content)
            # Add .encrypted extension to indicate encrypted file
            unique_filename = f"{unique_filename}.encrypted"

        # Save file
        file_path = user_dir / unique_filename
        await self._write_file(file_path, content)

        # Return relative path
        return str(file_path.relative_to(self.upload_dir.parent))

    async def read_file(self, file_path: str, decrypt: bool = True) -> bytes:
        """Read and optionally decrypt a file.

        Args:
            file_path: Relative file path
            decrypt: Whether to decrypt the file (default: True)

        Returns:
            File content (decrypted if decrypt=True)

        Raises:
            ValueError: If decryption fails
        """
        full_path = self._resolve_relative_path(file_path)

        if not full_path.exists() or not full_path.is_file():
            raise ValueError(f"File not found: {file_path}")

        content = await asyncio.to_thread(full_path.read_bytes)

        # Decrypt if file is encrypted and decryption is requested
        if decrypt and file_path.endswith(".encrypted") and self.encryption_service:
            try:
                content = self.encryption_service.decrypt(content)
            except ValueError as e:
                raise ValueError(f"Failed to decrypt file: {e}")

        return content

    async def save_multiple_files(
        self, files: list[UploadFile], user_id: str
    ) -> list[str]:
        """Save multiple files with encryption.

        Args:
            files: List of uploaded files
            user_id: User identifier

        Returns:
            List of relative file paths
        """
        file_paths = []
        for file in files:
            try:
                file_path = await self.save_file(file, user_id)
                file_paths.append(file_path)
            except ValueError as e:
                # Log error but continue with other files
                logging.getLogger(__name__).error(
                    "Error saving file %s: %s", file.filename, e
                )
                continue

        return file_paths

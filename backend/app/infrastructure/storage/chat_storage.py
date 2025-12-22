"""File upload service for chat attachments."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile


import logging

class ChatFileUploadService:
    """Service for handling chat file uploads."""

    def __init__(self, upload_dir: str = "uploads/chat"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Allowed file types
        self.allowed_image_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
        }
        self.allowed_file_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "application/zip",
        }

        # Max file sizes (in bytes)
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.max_file_size = 50 * 1024 * 1024  # 50MB

    def validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """Validate uploaded file."""
        # Check file type
        if file.content_type not in (
            self.allowed_image_types | self.allowed_file_types
        ):
            return False, f"File type {file.content_type} not allowed"

        # Check file size
        max_size = (
            self.max_image_size
            if file.content_type in self.allowed_image_types
            else self.max_file_size
        )

        # Note: file.size might not be available, so we'll check during read
        return True, "OK"

    async def save_file(
        self, file: UploadFile, user_id: str, room_id: str
    ) -> tuple[str, str]:
        """Save uploaded file and return (file_path, file_url)."""
        # Validate
        is_valid, error = self.validate_file(file)
        if not is_valid:
            raise ValueError(error)

        # Generate unique filename
        file_ext = Path(file.filename or "file").suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Create user/room directory structure
        date_dir = datetime.now().strftime("%Y/%m/%d")
        file_dir = self.upload_dir / date_dir / room_id
        file_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = file_dir / unique_filename
        content = await file.read()

        # Check size
        max_size = (
            self.max_image_size
            if file.content_type in self.allowed_image_types
            else self.max_file_size
        )
        if len(content) > max_size:
            raise ValueError(
                f"File size {len(content)} exceeds maximum {max_size} bytes"
            )

        with open(file_path, "wb") as f:
            f.write(content)

        # Generate URL
        relative_path = file_path.relative_to(self.upload_dir)
        file_url = f"/uploads/chat/{relative_path}"

        return str(file_path), file_url

    async def save_multiple_files(
        self, files: list[UploadFile], user_id: str, room_id: str
    ) -> list[tuple[str, str]]:
        """Save multiple files and return list of (file_path, file_url)."""
        results = []
        for file in files:
            try:
                file_path, file_url = await self.save_file(file, user_id, room_id)
                results.append((file_path, file_url))
            except Exception as e:
                # Log error but continue with other files
                logging.getLogger(__name__).error(f"Error saving file {file.filename}: {e}")
                continue
        return results

    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            logging.getLogger(__name__).error(f"Error deleting file {file_path}: {e}")
            return False

    def get_file_type(self, content_type: str) -> str:
        """Get file type category."""
        if content_type in self.allowed_image_types:
            return "image"
        return "file"

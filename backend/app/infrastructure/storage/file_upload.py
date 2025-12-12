"""File upload utilities for ranking system."""

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile


class FileUploadService:
    """Service for handling file uploads."""

    def __init__(self, upload_dir: str = "uploads/verification"):
        """Initialize file upload service."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def validate_file(self, file: UploadFile) -> tuple[bool, Optional[str]]:
        """Validate uploaded file."""
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}"

        # Check file size (if available)
        if file.size and file.size > self.max_file_size:
            return False, f"File too large. Maximum size: {self.max_file_size / 1024 / 1024}MB"

        return True, None

    async def save_file(self, file: UploadFile, team_id: str) -> str:
        """Save uploaded file and return file path."""
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)

        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{team_id}_{uuid.uuid4().hex}{file_ext}"

        # Create team directory
        team_dir = self.upload_dir / team_id
        team_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = team_dir / unique_filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Return relative path
        return str(file_path.relative_to(self.upload_dir.parent))

    async def save_multiple_files(
        self, files: list[UploadFile], team_id: str
    ) -> list[str]:
        """Save multiple files and return list of file paths."""
        file_paths = []
        for file in files:
            try:
                file_path = await self.save_file(file, team_id)
                file_paths.append(file_path)
            except ValueError as e:
                # Log error but continue with other files
                print(f"Error saving file {file.filename}: {e}")
                continue

        return file_paths

    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            full_path = self.upload_dir.parent / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """Get URL for accessing file."""
        # For local storage, return relative path
        # For S3, this would return the S3 URL
        return f"/uploads/{file_path}"


# S3 Upload Service (for production)
class S3UploadService:
    """Upload service using AWS S3."""

    def __init__(self, bucket_name: str):
        """Initialize S3 client."""
        self.bucket_name = bucket_name
            raise ValueError(error_msg)

        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"verification/{team_id}/{uuid.uuid4().hex}{file_ext}"

        # TODO: Upload to S3
        # content = await file.read()
        # self.s3_client.put_object(
        #     Bucket=self.bucket_name,
        #     Key=unique_filename,
        #     Body=content,
        #     ContentType=file.content_type
        # )

        # Return S3 URL
        return f"https://{self.bucket_name}.s3.{self.aws_region}.amazonaws.com/{unique_filename}"

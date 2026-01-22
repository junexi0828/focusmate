"""File upload utilities for ranking system."""

import asyncio
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings

class FileUploadService:
    """Service for handling file uploads."""

    def __init__(self, upload_dir: str = "uploads/verification"):
        """Initialize file upload service."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
        self.max_file_size = settings.STORAGE_MAX_FILE_SIZE

    def _safe_dir_name(self, name: str) -> str:
        """Normalize directory name to prevent path traversal."""
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", name or "").strip("_")
        return safe or uuid.uuid4().hex

    def _resolve_relative_path(self, file_path: str) -> Path:
        """Resolve and validate a relative path under uploads root."""
        candidate = Path(file_path)
        if candidate.is_absolute():
            raise ValueError("Absolute paths are not allowed")
        base_dir = self.upload_dir.parent.resolve()
        resolved = (base_dir / candidate).resolve()
        if resolved != base_dir and base_dir not in resolved.parents:
            raise ValueError("Path traversal detected")
        return resolved

    def validate_file(self, file: UploadFile) -> tuple[bool, str | None]:
        """Validate uploaded file."""
        # Check file extension
        file_ext = Path(file.filename or "upload").suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}"

        # Check file size (if available)
        size = getattr(file, "size", None)
        if size and size > self.max_file_size:
            return False, f"File too large. Maximum size: {self.max_file_size / 1024 / 1024}MB"

        return True, None

    async def _read_with_limit(self, file: UploadFile) -> bytes:
        """Read file content with size limit enforcement."""
        chunks: list[bytes] = []
        total = 0
        chunk_size = 1024 * 1024
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > self.max_file_size:
                raise ValueError(
                    f"File too large. Maximum size: {self.max_file_size / 1024 / 1024}MB"
                )
            chunks.append(chunk)
        return b"".join(chunks)

    async def _write_file(self, path: Path, content: bytes) -> None:
        """Write file content without blocking the event loop."""
        await asyncio.to_thread(path.write_bytes, content)

    async def save_file(self, file: UploadFile, team_id: str) -> str:
        """Save uploaded file and return file path."""
        # Validate file
        is_valid, error_msg = self.validate_file(file)
        if not is_valid:
            raise ValueError(error_msg)

        # Generate unique filename
        file_ext = Path(file.filename or "upload").suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"

        # Create team directory
        safe_team_id = self._safe_dir_name(team_id)
        team_dir = self.upload_dir / safe_team_id
        team_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = team_dir / unique_filename
        content = await self._read_with_limit(file)
        await self._write_file(file_path, content)

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
                logging.getLogger(__name__).error(f"Error saving file {file.filename}: {e}")
                continue

        return file_paths

    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            full_path = self._resolve_relative_path(file_path)
            if full_path.exists() and full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            logging.getLogger(__name__).error(
                "Error deleting file %s: %s", file_path, e
            )
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
        import boto3
        from botocore.exceptions import ClientError

        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        self.ClientError = ClientError
        self.datetime = datetime
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
        self.max_file_size = settings.STORAGE_MAX_FILE_SIZE

    def _safe_dir_name(self, name: str) -> str:
        """Normalize directory name to prevent path traversal."""
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", name or "").strip("_")
        return safe or uuid.uuid4().hex

    def _validate_file(self, file: UploadFile) -> None:
        file_ext = Path(file.filename or "upload").suffix.lower()
        if file_ext not in self.allowed_extensions:
            raise ValueError(f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}")

    async def _read_with_limit(self, file: UploadFile) -> bytes:
        """Read file content with size limit enforcement."""
        chunks: list[bytes] = []
        total = 0
        chunk_size = 1024 * 1024
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > self.max_file_size:
                raise ValueError(
                    f"File too large. Maximum size: {self.max_file_size / 1024 / 1024}MB"
                )
            chunks.append(chunk)
        return b"".join(chunks)

    async def save_file(self, file: UploadFile, user_id: str) -> tuple[str, str]:
        """Upload file to S3."""
        try:
            self._validate_file(file)
            # Generate unique filename
            file_ext = Path(file.filename or "file").suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_ext}"

            # Create S3 key with user directory structure
            safe_user_id = self._safe_dir_name(user_id)
            date_dir = self.datetime.now().strftime("%Y/%m/%d")
            s3_key = f"uploads/{safe_user_id}/{date_dir}/{unique_filename}"

            # Read file content
            content = await self._read_with_limit(file)

            # Upload to S3
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type or "application/octet-stream",
            )

            # Generate URL
            region = os.getenv("AWS_REGION", "us-east-1")
            file_url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{s3_key}"

            return s3_key, file_url

        except self.ClientError as e:
            raise ValueError(f"S3 upload failed: {e}")

    async def save_multiple_files(
        self, files: list[UploadFile], user_id: str
    ) -> list[tuple[str, str]]:
        """Upload multiple files to S3."""
        results = []
        for file in files:
            try:
                s3_key, file_url = await self.save_file(file, user_id)
                results.append((s3_key, file_url))
            except Exception as e:
                logging.getLogger(__name__).error(
                    "Error uploading file %s: %s", file.filename, e
                )
                continue
        return results

    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except self.ClientError as e:
            logging.getLogger(__name__).error("Error deleting file %s: %s", s3_key, e)
            return False

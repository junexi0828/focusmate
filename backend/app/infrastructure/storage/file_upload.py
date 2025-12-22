"""File upload utilities for ranking system."""

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile


import logging

class FileUploadService:
    """Service for handling file uploads."""

    def __init__(self, upload_dir: str = "uploads/verification"):
        """Initialize file upload service."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def validate_file(self, file: UploadFile) -> tuple[bool, str | None]:
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
                logging.getLogger(__name__).error(f"Error saving file {file.filename}: {e}")
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
            logging.getLogger(__name__).error(f"Error deleting file {file_path}: {e}")
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

    async def save_file(self, file: UploadFile, user_id: str) -> tuple[str, str]:
        """Upload file to S3."""
        try:
            # Generate unique filename
            file_ext = Path(file.filename or "file").suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"

            # Create S3 key with user directory structure
            date_dir = self.datetime.now().strftime("%Y/%m/%d")
            s3_key = f"uploads/{user_id}/{date_dir}/{unique_filename}"

            # Read file content
            content = await file.read()

            # Upload to S3
            self.s3_client.put_object(
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
                logging.getLogger(__name__).error(f"Error uploading file {file.filename}: {e}")
                continue
        return results

    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except self.ClientError as e:
            logging.getLogger(__name__).error(f"Error deleting file {s3_key}: {e}")
            return False

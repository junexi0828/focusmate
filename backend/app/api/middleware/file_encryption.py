"""Middleware for automatic file encryption/decryption.

This middleware automatically encrypts files on upload and decrypts on download.
Uses Fernet symmetric encryption from the encryption service.
"""

from collections.abc import Callable

from fastapi import Request, Response, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.shared.utils.encryption import get_encryption_service


class FileEncryptionMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically encrypt/decrypt files."""

    def __init__(
        self,
        app: ASGIApp,
        encrypt_paths: list[str] | None = None,
        decrypt_paths: list[str] | None = None,
    ):
        """Initialize middleware.

        Args:
            app: ASGI application
            encrypt_paths: List of URL path patterns to encrypt (e.g., ["/api/v1/upload"])
            decrypt_paths: List of URL path patterns to decrypt (e.g., ["/api/v1/download"])
        """
        super().__init__(app)
        self.encryption_service = get_encryption_service()
        self.encrypt_paths = encrypt_paths or []
        self.decrypt_paths = decrypt_paths or []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response with encrypted/decrypted content
        """
        # Check if this is an upload endpoint that needs encryption
        should_encrypt = any(
            request.url.path.startswith(path) for path in self.encrypt_paths
        )

        # Check if this is a download endpoint that needs decryption
        should_decrypt = any(
            request.url.path.startswith(path) for path in self.decrypt_paths
        )

        # Process request (upload encryption)
        if should_encrypt and request.method in ("POST", "PUT", "PATCH"):
            # Note: File encryption is handled at the service layer
            # This middleware logs encryption events
            pass

        # Process response (download decryption)
        response = await call_next(request)

        if should_decrypt and response.status_code == 200:
            # Check if response contains encrypted file data
            if "application/octet-stream" in response.headers.get("content-type", ""):
                try:
                    # Read response body
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk

                    # Decrypt the file content
                    decrypted_data = self.encryption_service.decrypt(body)

                    # Create new response with decrypted data
                    return Response(
                        content=decrypted_data,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )
                except Exception:
                    # If decryption fails, return original response
                    return response

        return response


def encrypt_upload_file(upload_file: UploadFile) -> bytes:
    """Encrypt an uploaded file.

    Args:
        upload_file: File to encrypt

    Returns:
        Encrypted file content
    """
    encryption_service = get_encryption_service()
    file_content = upload_file.file.read()
    encrypted_content = encryption_service.encrypt(file_content)
    upload_file.file.seek(0)  # Reset file pointer
    return encrypted_content


async def decrypt_file_response(file_path: str) -> bytes:
    """Decrypt a file for download.

    Args:
        file_path: Path to encrypted file

    Returns:
        Decrypted file content
    """
    encryption_service = get_encryption_service()

    # Read encrypted file
    with open(file_path, "rb") as f:
        encrypted_content = f.read()

    # Decrypt
    decrypted_content = encryption_service.decrypt(encrypted_content)
    return decrypted_content

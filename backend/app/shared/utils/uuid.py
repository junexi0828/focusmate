"""UUID generation utilities."""

import uuid


def generate_uuid() -> str:
    """Generate a new UUID string.
    
    Returns:
        UUID as string
    """
    return str(uuid.uuid4())

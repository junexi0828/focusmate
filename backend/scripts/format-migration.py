#!/usr/bin/env python3
"""Format migration file using ruff (if available).

This script is used as an Alembic post-write hook. It gracefully handles
the case where ruff is not installed.

Alembic sets the REVISION_SCRIPT_FILENAME environment variable with the
path to the generated migration file.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Format migration file if ruff is available."""
    # Get file path from environment variable (set by Alembic) or command line
    file_path_str = os.environ.get("REVISION_SCRIPT_FILENAME")

    if not file_path_str and len(sys.argv) > 1:
        file_path_str = sys.argv[1]

    if not file_path_str:
        # No file path provided, exit silently
        sys.exit(0)

    file_path = Path(file_path_str)

    if not file_path.exists():
        # File doesn't exist, exit silently
        sys.exit(0)

    try:
        # Try to format with ruff
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", str(file_path)],
            capture_output=True,
            text=True,
            timeout=10, check=False,
        )

        if result.returncode == 0:
            # Successfully formatted
            sys.exit(0)
        else:
            # Ruff failed, but don't fail the migration
            # This can happen if ruff is not installed or there's a syntax error
            sys.exit(0)

    except FileNotFoundError:
        # ruff module not found - skip formatting
        sys.exit(0)
    except subprocess.TimeoutExpired:
        # Formatting took too long - skip
        sys.exit(0)
    except Exception:
        # Any other error - skip formatting silently
        sys.exit(0)


if __name__ == "__main__":
    main()

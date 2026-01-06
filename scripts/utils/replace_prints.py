#!/usr/bin/env python3
"""Replace print() statements with logging in Python files."""

import re
import sys
from pathlib import Path

def add_logging_import(content: str) -> str:
    """Add logging import if not present."""
    if "import logging" in content:
        return content

    # Find the first import statement
    lines = content.split("\n")
    import_index = -1
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            import_index = i
            break

    if import_index >= 0:
        # Add after first import block
        for i in range(import_index, len(lines)):
            if not lines[i].startswith(("import ", "from ", " ", "\t")) and lines[i].strip():
                lines.insert(i, "import logging")
                lines.insert(i + 1, "")
                break
    else:
        # Add at the beginning after docstring
        if lines[0].startswith('"""') or lines[0].startswith("'''"):
            for i in range(1, len(lines)):
                if lines[i].endswith('"""') or lines[i].endswith("'''"):
                    lines.insert(i + 2, "import logging")
                    lines.insert(i + 3, "")
                    break

    return "\n".join(lines)

def replace_print_with_logging(content: str, filename: str) -> tuple[str, int]:
    """Replace print() with logging.error()."""
    # Pattern to match print statements
    pattern = r'(\s*)print\(f?"([^"]*)"(?:\s*\.\s*format\([^)]*\))?\)'

    replacements = 0

    def replacement(match):
        nonlocal replacements
        indent = match.group(1)
        message = match.group(2)

        # Convert to logging
        replacements += 1
        return f'{indent}logging.getLogger(__name__).error(f"{message}")'

    new_content = re.sub(pattern, replacement, content)

    # Add logging import if we made replacements
    if replacements > 0:
        new_content = add_logging_import(new_content)

    return new_content, replacements

def main():
    """Main function."""
    files_to_fix = [
        "backend/app/api/v1/endpoints/chat.py",
        "backend/app/api/v1/endpoints/room_reservations.py",
        "backend/app/api/middleware/rate_limit.py",
        "backend/app/infrastructure/redis/pubsub_manager.py",
        "backend/app/infrastructure/storage/chat_storage.py",
        "backend/app/infrastructure/storage/encrypted_file_upload.py",
        "backend/app/infrastructure/storage/file_upload.py",
        "backend/app/domain/achievement/service.py",
        "backend/app/domain/verification/service.py",
    ]

    total_replacements = 0

    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        content = path.read_text()
        new_content, count = replace_print_with_logging(content, file_path)

        if count > 0:
            path.write_text(new_content)
            print(f"✅ {file_path}: {count} replacements")
            total_replacements += count
        else:
            print(f"ℹ️  {file_path}: No print statements found")

    print(f"\n🎉 Total replacements: {total_replacements}")
    return 0 if total_replacements > 0 else 1

if __name__ == "__main__":
    sys.exit(main())

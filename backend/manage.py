#!/usr/bin/env python3
"""Focus Mate Backend - Management Script

Unified management script for server, testing, migrations, and database management.

Usage:
    python manage.py [command] [options]

Commands:
    runserver      - Run development server
    test           - Run tests
    migrate        - Create database migration
    upgrade        - Apply migrations
    downgrade      - Rollback migrations
    reset-db       - Reset database
    shell          - Start Python shell
    check          - Code quality check (lint, type check)
    seed           - Generate test data
    health         - Health check

Examples:
    python manage.py runserver              # Start dev server
    python manage.py runserver --port 9000  # Change port
    python manage.py test                   # Run all tests
    python manage.py test tests/test_auth.py  # Run specific test
    python manage.py migrate "add user table"  # Create migration
    python manage.py upgrade                # Apply migrations
    python manage.py reset-db               # Reset & recreate DB
    python manage.py seed                   # Generate test data
    python manage.py check                  # Code quality check
"""

import asyncio
import sys
from pathlib import Path


# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_banner(text: str):
    """Print banner"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def runserver(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run development server"""
    import uvicorn

    print_banner("Focus Mate Backend Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(
        f"API Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs\n"
    )

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


def test(path: str = "tests/", verbose: bool = False):
    """Run tests"""
    import subprocess

    print_banner("Running Tests")

    cmd = ["pytest", path]
    if verbose:
        cmd.append("-v")
    cmd.extend(["--cov=app", "--cov-report=term-missing"])

    result = subprocess.run(cmd, check=False)
    sys.exit(result.returncode)


def migrate(message: str):
    """Create Alembic migration"""
    import subprocess

    if not message:
        print("Error: Migration message is required")
        print('Usage: python manage.py migrate "your message"')
        sys.exit(1)

    print_banner("Creating Database Migration")
    print(f"Message: {message}\n")

    result = subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=False)

    if result.returncode == 0:
        print("\nMigration created successfully")
        print("Run 'python manage.py upgrade' to apply migration")
    else:
        print("\nMigration creation failed")
        sys.exit(1)


def upgrade(revision: str = "head"):
    """Apply migrations"""
    import subprocess

    print_banner("Applying Database Migrations")
    print(f"Target: {revision}\n")

    result = subprocess.run(["alembic", "upgrade", revision], check=False)

    if result.returncode == 0:
        print("\nMigration applied successfully")
    else:
        print("\nMigration failed")
        sys.exit(1)


def downgrade(revision: str = "-1"):
    """Rollback migration"""
    import subprocess

    print_banner("Rolling Back Database Migration")
    print(f"Target: {revision}\n")

    result = subprocess.run(["alembic", "downgrade", revision], check=False)

    if result.returncode == 0:
        print("\nMigration rolled back successfully")
    else:
        print("\nRollback failed")
        sys.exit(1)


async def _reset_db():
    """Reset database (internal function)"""
    from sqlalchemy import text

    import app.infrastructure.database.models  # noqa: F401 - Discover all models for metadata
    from app.infrastructure.database.base import Base
    from app.infrastructure.database.session import engine

    print("Dropping all tables with CASCADE...")
    async with engine.begin() as conn:
        # Handle PostgreSQL CASCADE if using postgres
        if engine.url.drivername.startswith("postgresql"):
            result = await conn.execute(text(
                "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"
            ))
            tables = [f'"{row[0]}"' for row in result]
            if tables:
                await conn.execute(text(f"DROP TABLE IF EXISTS {', '.join(tables)} CASCADE"))
        else:
            await conn.run_sync(Base.metadata.drop_all)

    print("Tables dropped")

    print("Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables created")

    await engine.dispose()


def reset_db(confirm: bool = False):
    """Reset database"""
    print_banner("Database Reset")

    if not confirm:
        response = input(
            "Are you sure you want to reset the database? This will delete all data. (yes/no): "
        )
        if response.lower() != "yes":
            print("Database reset cancelled")
            return

    asyncio.run(_reset_db())
    print("\nDatabase reset successfully")


def seed():
    """Generate comprehensive test data using enhanced seed script"""
    from scripts.seed_comprehensive import seed_comprehensive_data

    print_banner("Seeding Comprehensive Test Data")
    asyncio.run(seed_comprehensive_data())


def shell():
    """Start Python shell"""
    import code

    print_banner("Python Shell")
    print("Available imports:")
    print("  - AsyncSessionLocal")
    print("  - settings")
    print("  - models (User, Room, Timer, etc.)")
    print()

    # Import commonly used modules
    from app.core.config import settings
    from app.infrastructure.database import models
    from app.infrastructure.database.session import AsyncSessionLocal

    local_vars = {
        "AsyncSessionLocal": AsyncSessionLocal,
        "settings": settings,
        "models": models,
    }

    code.interact(local=local_vars)


def check():
    """Code quality check"""
    import subprocess

    print_banner("Code Quality Check")

    checks = [
        ("Running Ruff linter", ["ruff", "check", "app"]),
        ("Running MyPy type checker", ["mypy", "app"]),
    ]

    failed = []

    for name, cmd in checks:
        print(f"\n{name}...")
        result = subprocess.run(cmd, capture_output=True, check=False)
        if result.returncode != 0:
            failed.append(name)
            print(f"{name} failed")
        else:
            print(f"{name} passed")

    if failed:
        print(f"\n{len(failed)} check(s) failed:")
        for check in failed:
            print(f"  - {check}")
        sys.exit(1)
    else:
        print("\nAll checks passed!")


def health():
    """Server health check"""
    import httpx

    print_banner("Health Check")

    url = "http://localhost:8000/health"
    print(f"Checking: {url}")

    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print("\nServer is healthy")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Environment: {data.get('environment')}")
        else:
            print(f"\nServer returned status code: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"\nHealth check failed: {e}")
        print("Make sure the server is running: python manage.py runserver")
        sys.exit(1)


def show_help():
    """Show help"""
    print(__doc__)


def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "runserver": lambda: runserver(
            host=args[args.index("--host") + 1] if "--host" in args else "0.0.0.0",
            port=int(args[args.index("--port") + 1]) if "--port" in args else 8000,
            reload="--no-reload" not in args,
        ),
        "test": lambda: test(
            path=args[0] if args else "tests/",
            verbose="-v" in args or "--verbose" in args,
        ),
        "migrate": lambda: migrate(args[0] if args else ""),
        "upgrade": lambda: upgrade(args[0] if args else "head"),
        "downgrade": lambda: downgrade(args[0] if args else "-1"),
        "reset-db": lambda: reset_db(confirm="--yes" in args),
        "seed": seed,
        "shell": shell,
        "check": check,
        "health": health,
        "help": show_help,
        "--help": show_help,
        "-h": show_help,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print("Run 'python manage.py help' for usage information")
        sys.exit(1)

    try:
        commands[command]()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

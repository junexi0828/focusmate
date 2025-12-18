# Focus Mate Backend - Troubleshooting Guide

## Python Version Issues

### Error: Python 3.14 compatibility issues

**Problem**: `pydantic-core` fails to build with Python 3.14

**Error Message**:

```
error: the configured Python interpreter version (3.14) is newer than PyO3's maximum supported version (3.13)
```

**Solutions**:

1. **Recommended: Use Python 3.12 or 3.13**

   ```bash
   # Install Python 3.13 using pyenv
   pyenv install 3.13.0
   pyenv local 3.13.0

   # Or use Homebrew
   brew install python@3.13
   ```

2. **Workaround for Python 3.14** (not recommended):

   ```bash
   export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
   pip install -r requirements.txt
   ```

3. **Check Python version**:
   ```bash
   python3 --version
   # Should show: Python 3.12.x or Python 3.13.x
   ```

### Python version not found

**Problem**: `python3` command not found

**Solutions**:

```bash
# macOS
brew install python@3.13

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.13 python3.13-venv

# Verify installation
python3.13 --version
```

---

## Dependency Installation Issues

### Failed to build pydantic-core

**Problem**: Native extension build fails

**Solutions**:

1. **Install build dependencies**:

   ```bash
   # macOS
   xcode-select --install
   brew install rust

   # Linux
   sudo apt install build-essential python3-dev
   ```

2. **Use pre-built wheels**:

   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. **Clear pip cache**:
   ```bash
   pip cache purge
   pip install -r requirements.txt
   ```

### Import errors after installation

**Problem**: Module not found errors

**Solutions**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## Environment Configuration Issues

### .env file not found

**Problem**: Application can't find environment variables

**Solution**:

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### SECRET_KEY not set

**Problem**: Security warnings about SECRET_KEY

**Solution**:

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Add to .env
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')" >> .env
```

---

## Database Issues

### Database locked (SQLite)

**Problem**: SQLite database is locked

**Solutions**:

1. **Enable WAL mode** (recommended):

   ```python
   # In your database URL
   DATABASE_URL=sqlite+aiosqlite:///./focus_mate.db?mode=rwc
   ```

2. **Use PostgreSQL** (production):

   ```bash
   # Update .env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/focus_mate
   ```

3. **Check for other processes**:
   ```bash
   lsof focus_mate.db
   ```

### Migration errors

**Problem**: Alembic migration fails

**Solutions**:

```bash
# Check migration status
alembic current

# View migration history
alembic history

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

---

## Port Already in Use

### Port 8000 already in use

**Problem**: Can't start server, port is occupied

**Solutions**:

1. **Find and kill process**:

   ```bash
   # macOS/Linux
   lsof -ti:8000 | xargs kill -9

   # Or use different port
   uvicorn app.main:app --reload --port 8001
   ```

2. **Update .env**:
   ```bash
   PORT=8001
   ```

---

## Virtual Environment Issues

### Virtual environment not activating

**Problem**: `source venv/bin/activate` doesn't work

**Solutions**:

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Verify activation
which python  # Should point to venv/bin/python
```

### Wrong Python in virtual environment

**Problem**: venv uses wrong Python version

**Solutions**:

```bash
# Remove and recreate with specific Python version
rm -rf venv
python3.13 -m venv venv  # Use specific version
source venv/bin/activate
python --version  # Verify version
```

---

## Quick Fixes

### Complete reset

```bash
# Remove virtual environment and database
rm -rf venv
rm -f focus_mate.db

# Recreate everything
./run.sh
```

### Reinstall all dependencies

```bash
source venv/bin/activate
pip install --upgrade pip
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## Getting Help

If you're still experiencing issues:

1. Check the [Development Guide](./docs/DEVELOPMENT.md)
2. Review [Architecture Documentation](./docs/ARCHITECTURE.md)
3. Check application logs
4. Verify Python version compatibility
5. Ensure all dependencies are installed

---

**Last Updated**: 2025-12-04

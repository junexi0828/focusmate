# Focus Mate Backend - Development Guide

## Overview

This guide covers development workflow, best practices, and implementation details for the Focus Mate backend.

---

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/focus-mate.git
cd focus-mate/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env

# Initialize database
alembic upgrade head
```

### 2. Running Development Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Or use the quick start script
./run.sh
```

### 3. Code Style

- **Linter**: Ruff (configured in `pyproject.toml`)
- **Formatter**: Ruff Format
- **Type Checker**: MyPy (strict mode)
- **Complexity Limit**: CC < 10

### 4. Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD)
3. Implement feature
4. Run quality checks
5. Commit with conventional commits
6. Create pull request

---

## Adding New Features

### 1. Create Domain Module

```bash
# Create domain structure
mkdir -p app/domain/{feature_name}
touch app/domain/{feature_name}/__init__.py
touch app/domain/{feature_name}/schemas.py
touch app/domain/{feature_name}/service.py
```

### 2. Create Repository

```bash
touch app/infrastructure/repositories/{feature}_repository.py
```

### 3. Create API Endpoint

```bash
touch app/api/v1/endpoints/{feature}.py
```

### 4. Create Database Model

```bash
touch app/infrastructure/database/models/{feature}.py
```

### 5. Create Migration

```bash
alembic revision --autogenerate -m "Add {feature} table"
alembic upgrade head
```

### 6. Write Tests

```bash
touch tests/unit/domain/test_{feature}_service.py
touch tests/integration/api/test_{feature}_api.py
```

---

## Database Migrations

### Create Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user table"

# Create empty migration
alembic revision -m "Add user table"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision>

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision>
```

### View Migration History

```bash
# List all migrations
alembic history

# Show current revision
alembic current
```

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Run specific test file
pytest tests/unit/domain/test_room_service.py

# Run with verbose output
pytest -v
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Writing Tests

**Unit Test Example**:
```python
# tests/unit/domain/test_room_service.py
import pytest
from app.domain.room.service import RoomService
from app.domain.room.schemas import RoomCreate

@pytest.mark.asyncio
async def test_create_room():
    service = RoomService(mock_repository)
    data = RoomCreate(name="test-room", work_duration=25)
    result = await service.create_room(data)
    assert result.name == "test-room"
```

**Integration Test Example**:
```python
# tests/integration/api/test_rooms_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_room_endpoint(client: AsyncClient):
    response = await client.post("/api/v1/rooms", json={
        "name": "test-room",
        "work_duration": 25
    })
    assert response.status_code == 201
```

---

## Quality Checks

### Type Checking

```bash
# Run MyPy
mypy app/ --strict

# Check specific file
mypy app/domain/room/service.py
```

### Linting

```bash
# Check code
ruff check app/

# Auto-fix issues
ruff check --fix app/

# Format code
ruff format app/
```

### Security Scanning

```bash
# Run Bandit security scanner
bandit -r app/

# With specific configuration
bandit -r app/ -c pyproject.toml
```

### Run All Quality Checks

```bash
# Run all checks
ruff check app/
mypy app/ --strict
pytest --cov=app
```

---

## Debugging

### Enable Debug Logging

```bash
# Set log level in .env
APP_LOG_LEVEL=DEBUG

# Or via environment variable
APP_LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

### Database Debugging

```bash
# Enable SQL query logging
# Add to .env
SQLALCHEMY_ECHO=true
```

### Using Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

---

## Frontend Integration

### API Client Setup

```typescript
// Frontend API configuration
const API_BASE_URL = "http://localhost:8000/api/v1";

// Example: Create room
const createRoom = async (data: RoomCreate) => {
  const response = await fetch(`${API_BASE_URL}/rooms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return response.json();
};
```

### WebSocket Connection

```typescript
// Frontend WebSocket setup
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/{room_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle message types: timer_update, participant_joined, etc.
};
```

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Database Issues

```bash
# Reset database (development only!)
rm focus_mate.db

# Re-run migrations
alembic upgrade head
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Type Checking Errors

```bash
# Clear MyPy cache
rm -r .mypy_cache

# Re-run type checking
mypy app/ --strict
```

---

## Performance Optimization

### Database Queries

- Use eager loading to prevent N+1 queries
- Add indexes on frequently queried fields
- Use pagination for large result sets
- Cache frequently accessed data

### API Response Time

- Minimize database queries
- Use async/await for I/O operations
- Implement response caching where appropriate
- Optimize serialization (Pydantic models)

### WebSocket Performance

- Limit connection per room
- Implement connection pooling
- Use Redis Pub/Sub for scaling
- Add heartbeat/ping-pong mechanism

---

## Code Review Checklist

- [ ] Code follows style guide (Ruff)
- [ ] Type hints are complete (MyPy passes)
- [ ] Tests are written and passing
- [ ] Test coverage is > 90%
- [ ] Documentation is updated
- [ ] No security vulnerabilities (Bandit)
- [ ] Database migrations are tested
- [ ] Error handling is appropriate
- [ ] Logging is adequate
- [ ] Performance is acceptable

---

## Best Practices

### Domain Layer

- Keep business logic in domain services
- Use Pydantic schemas for validation
- Define clear interfaces (Protocols)
- Keep domain models pure (no infrastructure dependencies)

### API Layer

- Use dependency injection
- Handle exceptions properly
- Return appropriate HTTP status codes
- Document endpoints with docstrings

### Infrastructure Layer

- Implement repository pattern
- Use async/await for I/O operations
- Handle connection pooling
- Implement proper error handling

### Testing

- Write tests first (TDD)
- Test edge cases
- Mock external dependencies
- Use fixtures for test data
- Keep tests fast and isolated

---

## Next Steps

### High Priority
1. **JWT Middleware**: Add authentication middleware to protect endpoints
2. **Alembic Migration**: Generate initial migration for all models
3. **Testing**: Unit tests for services, integration tests for APIs
4. **Error Handling**: Global exception handler middleware

### Medium Priority
5. **Streak Calculation**: Implement daily streak logic in Achievement system
6. **Email Verification**: Add email verification on registration
7. **Password Reset**: Add forgot password flow
8. **Rate Limiting**: Add rate limiting middleware
9. **File Upload**: Add profile picture upload

### Low Priority
10. **Search Optimization**: Full-text search with PostgreSQL
11. **Notifications**: Push notifications for achievements, messages
12. **Analytics**: User activity tracking and metrics
13. **Admin Panel**: Admin endpoints for moderation

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://www.cosmicpython.com/)

---

**End of Development Guide**


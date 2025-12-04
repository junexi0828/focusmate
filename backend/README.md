# Focus Mate Backend

High-Assurance Team Pomodoro Platform - ISO/IEC 25010 Compliant Backend

## 🚀 Quick Start

### ⚡ Fast Track (Using Script)

```bash
# Navigate to backend directory
cd backend

# Run the quick start script
./run.sh
```

The script will automatically:

- Create `.env` from `.env.example`
- Set up Python virtual environment
- Install all dependencies
- Start the development server

### Prerequisites

- **Python 3.12 or 3.13** (Python 3.14 may have compatibility issues)
- Docker & Docker Compose (recommended)
- Redis (optional for local development)

> ⚠️ **Note**: Python 3.14 is not fully supported yet. Use Python 3.12 or 3.13 for best compatibility.
>
> **If you have Python 3.14 issues**: Run `./scripts/fix-python.sh` to recreate venv with compatible Python version.

### Manual Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/focus-mate.git
cd focus-mate/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
cp .env.example .env

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

### Docker Development

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Access Points

Once running, access:

- **API Base**: http://localhost:8000/api/v1
- **Health Check**: http://localhost:8000/health
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

> **Note**: Backend runs on port **8000** by default. You can change this in `.env` file.

## 📁 Project Structure

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed architecture documentation.

```
backend/
├── app/                    # Application code
│   ├── api/               # API endpoints (REST + WebSocket)
│   ├── core/              # Core infrastructure (config, security)
│   ├── domain/            # Business logic (DDD)
│   ├── infrastructure/    # External systems (DB, cache, etc.)
│   ├── application/       # Use cases
│   └── shared/            # Common utilities
├── tests/                 # Test suite
├── scripts/               # Utility scripts
└── docs/                  # Documentation
    ├── ARCHITECTURE.md    # Architecture & design patterns
    ├── API.md             # API reference
    └── DEVELOPMENT.md     # Development guide
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Run quality checks
mypy app/ --strict
ruff check app/
bandit -r app/
```

## 📊 Quality Metrics

| Metric                | Target | Current Status |
| :-------------------- | :----- | :------------- |
| Test Coverage         | > 90%  | TBD            |
| Type Safety           | 100%   | TBD            |
| Cyclomatic Complexity | < 10   | TBD            |
| Security Score        | A      | TBD            |

## 🔧 Development

### Code Style

- **Linter**: Ruff (configured in `pyproject.toml`)
- **Formatter**: Ruff Format
- **Type Checker**: MyPy (strict mode)
- **Complexity Limit**: CC < 10

### Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD)
3. Implement feature
4. Run quality checks
5. Commit with conventional commits
6. Create pull request

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

## 📚 Documentation

- **[Architecture](./docs/ARCHITECTURE.md)** - System design, patterns, and structure
- **[API Reference](./docs/API.md)** - Complete API documentation
- **[Development Guide](./docs/DEVELOPMENT.md)** - Development workflow and best practices

### Additional Resources

- **[Examples](./docs/examples/)** - Legacy documentation and implementation summaries (Korean)
  - `IMPLEMENTATION_SUMMARY.md` - 한국어 구현 요약
  - `BACKEND_IMPLEMENTATION_SUMMARY.md` - 상세 구현 문서
  - `PROJECT_STRUCTURE.md` - 프로젝트 구조 상세 설명
  - `API_QUICK_REFERENCE.md` - API 빠른 참조 (레거시)

### Interactive API Documentation

When the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Security

- **Authentication**: JWT tokens
- **Password Hashing**: Bcrypt
- **Input Validation**: Pydantic (strict mode)
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **CORS**: Configured for frontend domains

## 🚢 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable Redis for caching
- [ ] Configure CORS origins
- [ ] Set up HTTPS/SSL
- [ ] Enable rate limiting
- [ ] Configure monitoring (Prometheus/Sentry)
- [ ] Set `APP_ENV=production`
- [ ] Disable debug mode (`APP_DEBUG=false`)

### Docker Production Build

```bash
docker build -t focus-mate-backend:latest .
docker run -p 8000:8000 --env-file .env focus-mate-backend:latest
```

## 🔍 Troubleshooting

### Python Version Issues

If you encounter `pydantic-core` build errors with Python 3.14:

```bash
# Recommended: Use Python 3.12 or 3.13
python3.13 --version  # Check if available

# Or set compatibility flag (not recommended)
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
```

### Common Issues

- **Port already in use**: `lsof -ti:8000 | xargs kill -9`
- **Database locked**: Use PostgreSQL or enable WAL mode for SQLite
- **Import errors**: Ensure virtual environment is activated
- **.env not found**: Run `cp .env.example .env`

For detailed troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## 🤝 Contributing

1. Read [CONTRIBUTING.md](../docs/CONTRIBUTING.md)
2. Follow coding standards in [CODING_STANDARDS.md](../docs/CODING_STANDARDS.md)
3. Review [Development Guide](./docs/DEVELOPMENT.md) for workflow
4. Ensure 90%+ test coverage
5. Pass all quality gates

## 📄 License

MIT License - see [LICENSE](../LICENSE)

## 📞 Support

- GitHub Issues: [Report a bug](https://github.com/your-org/focus-mate/issues)
- Documentation: [Full docs](../docs/)
- Email: team@focusmate.com

# Robust NIDS Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Tests](https://github.com/Fidelisaboke/robust-nids/actions/workflows/ci.yml/badge.svg)](https://github.com/Fidelisaboke/robust-nids/actions)

## Project Overview

The **Robust NIDS Backend** is a FastAPI-powered API for a **Network Intrusion Detection System (NIDS)** designed to resist **adversarial evasion attacks**.
It supports adversarial training, explainable ML models (e.g., LIME/SHAP), and REST endpoints for monitoring, dataset management, and system configuration.

The backend integrates with a **Next.js frontend** and a **PostgreSQL database**, forming a modular, full-stack architecture.

## Key Features

- RESTful API built with **FastAPI**
- **Adversarially robust** ML pipeline (FGSM, PGD)
- **XGBoost**, **Autoencoder**, and ensemble classification
- **Dataset preprocessing**, imputation, and scaling
- **Authentication and authorization** with JWT tokens
- **PostgreSQL integration** with SQLAlchemy ORM
- **Alembic migrations** and seed scripts
- **Testing** via pytest with coverage reporting
- **Docker-ready** and **CI/CD integrated**

## Tech Stack

| Layer | Technology |
|--------|-------------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) |
| Machine Learning | scikit-learn, TensorFlow, XGBoost, Adversarial Robustness Toolbox |
| Database | PostgreSQL |
| Testing | pytest, httpx |
| Dependency Management | [uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Environment | Pydantic Settings |
| Containerization | Docker |

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/Fidelisaboke/robust-nids.git
cd robust-nids/backend
```

### 2. Create a Virtual Environment

Using **uv** (recommended):

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

### 5. Database Setup

Run the helper script or manual commands.

```bash
./scripts/setup_db.sh
```

Apply migrations:

```bash
alembic upgrade head
```

Seed initial data:

```bash
python database/seed.py
```

### 6. Run the Application

```bash
uvicorn api.main:app --reload
```

Access API docs:

* Swagger UI → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Structure

```
backend/
├── api/                # API route definitions (FastAPI routers)
├── core/               # Configuration, settings, security, logging
├── database/           # Models, schemas, seeding, migrations
├── ml/                 # ML pipeline, training, adversarial generation
├── scripts/            # Setup, dataset, and management scripts
├── tests/              # Unit and integration tests
├── .env.example        # Environment variable template
├── pyproject.toml      # Project dependencies and metadata
└── README.md           # Documentation
```

## Testing

Run all tests:

```bash
pytest -v
```

Run with coverage:

```bash
pytest --cov=api --cov-report=term-missing
```

Test HTTP routes:

```bash
pytest tests/test_routes.py
```

## CI/CD Integration

The backend integrates with **GitHub Actions** for automated:

* Code linting (`ruff`)
* Secret scanning (`detect-secrets`)
* Tests execution (`pytest`)
* Build validation

Pre-commit hooks are configured in `.pre-commit-config.yaml` and include:

* Ruff lint and auto-fix
* Prettier (for frontend)
* Detect-secrets scanning
* YAML and whitespace checks
* Pre-push backend tests

To install pre-commit:

```bash
pre-commit install
pre-commit install --hook-type pre-push
```

Run manually:

```bash
pre-commit run --all-files
```

## Common Commands

| Command                                   | Description                |
| ----------------------------------------- | -------------------------- |
| `uv run uvicorn api.main:app --reload`    | Run the backend locally    |
| `alembic upgrade head`                    | Apply latest DB migrations |
| `pytest`                                  | Run tests                  |
| `pytest --cov`                            | Run tests with coverage    |
| `ruff check .`                            | Lint code                  |
| `ruff format .`                           | Format code                |
| `detect-secrets scan > .secrets.baseline` | Generate secret baseline   |

## Dataset Configuration

The backend expects the **TII-SSRC-23 dataset** for training and evaluation.

Path convention:

```
data/raw/data.csv
data/processed/
```

Download manually or using:

```bash
python scripts/download_data.py
```

## Troubleshooting

**Issue:** Database connection errors
**Solution:** Verify `.env` `DATABASE_URL` and ensure PostgreSQL is running.

**Issue:** Alembic migration failure
**Solution:** Delete `alembic/versions/*` and reinitialize migrations.

**Issue:** ML model not found
**Solution:** Run training script under `ml/` to generate models.

## Deployment

### Local (manual)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Docker (recommended)

Build and run container:

```bash
docker compose up --build
```

### Production (Render / Railway / VPS)

* Set environment variables
* Configure PostgreSQL database
* Run migrations automatically on deploy

## License

This project is licensed under the **MIT License**.
See the [LICENSE](../LICENSE) file for more details.

## Acknowledgements

* [FastAPI](https://fastapi.tiangolo.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [scikit-learn](https://scikit-learn.org/)
* [TensorFlow](https://www.tensorflow.org/)
* [Adversarial Robustness Toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox)
* [uv](https://docs.astral.sh/uv/)
* [Alembic](https://alembic.sqlalchemy.org/)

# Adversarially Robust Network Intrusion Detection System (NIDS)

[![python-3.12](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/frontend-Next.js-black)](https://nextjs.org/)
[![CI Tests](https://github.com/Fidelisaboke/robust-nids/actions/workflows/ci.yml/badge.svg)](https://github.com/Fidelisaboke/robust-nids/actions/workflows/test.yml)

## Project Overview

A machine learning-based Network Intrusion Detection System designed to be resilient against adversarial evasion
attacks.
It integrates AI, cybersecurity analytics, and a modern full-stack architecture, combining a FastAPI backend for ML
inference and adversarial training with a Next.js dashboard for visualization, alerts, and analyst features

**Key Features:**

* **Adversarial Training:** Models are hardened against evasion attempts using state-of-the-art attacks from the
  Adversarial Robustness Toolbox (ART).
* **Dual Detection Strategy:** Combines a powerful XGBoost classifier for known attacks with an Autoencoder for
* detecting novel anomalies.
* **Analyst-in-the-Loop:** Includes a feedback mechanism for cybersecurity operators to label false
* positives/negatives, enabling iterative model refinement.
* **Explainable AI:** Integrates LIME to provide explanations for model predictions, building trust and understanding.
* **Live Monitoring Dashboard:** A modern, Next.js dashboard for real-time traffic analysis and alert visualization.

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Quick Install](#quick-install)
3. [Basic Usage](#basic-usage)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Acknowledgements](#acknowledgements)
7. [License](#license)

## Tech Stack

### Backend (API & ML Engine)

* **FastAPI**: High-performance REST API
* **SQLAlchemy + Alembic:** ORM and migrations
* **PostgreSQL:** Relational database
* **TensorFlow, XGBoost, Scikit-learn:** Model training & inference
* **Adversarial Robustness Toolbox (ART):** Adversarial sample generation
* **Docker:** Containerized deployment

### Frontend (Dashboard)

* **Next.js 15 (TypeScript)**: Modern React framework with App Router
* **Tailwind CSS:** Utility-first CSS framework
* **Recharts:** Charting library for data visualization
* **React Query:** Data fetching and state management
* **Axios:** HTTP client for API requests
* **React Hook Form + Zod:** Form handling and validation
* **Shadcn UI:** Pre-built accessible UI components

### Development & Deployment

* **Pre-commit Hooks:** enforced via `.pre-commit-config.yaml`
* **Linting:** `ruff` for Python, `eslint` + `prettier` for TypeScript
* **Testing:** `pytest` (backend)
* **CI/CD:** GitHub Actions (`.github/workflows/ci.yml`)
* **Containerization:** `backend/Dockerfile`
* **Package Manager:** `uv` for Python backend, `npm` for frontend

## Getting Started

### Prerequisites

* Python **3.12+**
* Node.js **18+**
* PostgreSQL (or Docker)
* Git
* Bash shell (Linux/WSL2 recommended)
* uv (Python project manager)

### Quick Install

- For detailed instructions, see [`docs/SETUP.md`](docs/SETUP.md).

#### Backend Setup (FastAPI)
- To quickly set up a Docker container, simply run (at project root):
```bash
./scripts/build-dev.sh
```

- Otherwise, follow the steps below for a local setup:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Fidelisaboke/robust-nids
   cd robust-nids/backend
   ```

2. **Create and activate a virtual environment:**

   ```bash
   uv venv
   source .venv/bin/activate  # Linux/WSL2/macOS
   # .venv\Scripts\activate   # Windows
   ```

3. **Install dependencies:**

   ```bash
   uv sync

   # Optionally, for dev and test dependencies
   uv sync --group dev --group test
   ```

4. **Set up environment variables:**

   ```bash
   cp .env.example .env # Configure your settings
   ```

5. **Run Alembic migrations:**

   ```bash
   alembic upgrade head
   ```

6. **Run database setup:**

   ```bash
   ./scripts/setup_db.sh
   ```

7. **Seed initial data (users, roles):**

   ```bash
   python database/seed.py
   ```

8. **Set up the dataset:** Follow the detailed instructions in [
   `docs/SETUP.md`](docs/SETUP.md#data-setup-tii-ssrc-23-dataset).

9. **Start the FastAPI server:**

   ```bash
   uvicorn api.main:app --reload
   ```

   Access the API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Frontend Setup (Next.js + TypeScript)
- It's preferred to run backend and frontend on separate terminal instances.

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Set up `.env`:**
   ```bash
   cp .env.local.example .env.local
   ```

3. **Run the development server:**

   ```bash
   npm run dev
   ```

   Visit the dashboard at: [http://localhost:3000](http://localhost:3000)

## Basic Usage

1. **Log In:**
   Access the web dashboard and authenticate using configured credentials.

2. **Monitor Traffic:**
   The dashboard provides:

    * **Real-time alerts** (via `/nids/alerts`)
    * **System logs** (via `/nids/logs`)
    * **Network metrics** and **visual analytics**

3. **Run Predictions:**
   Submit samples to `/nids/predict` to detect malicious activity.

4. **Trigger Adversarial Training:**
   Train models against evasion attacks using `/nids/train`.

5. **Review & Label:**
   Analysts can flag false positives/negatives, improving model feedback loops.

6. **Testing:**

   ```bash
   pytest -v
   ```

## Project Structure

```
robust-nids/
├── backend/                       # FastAPI backend (ML + API)
│   ├── api/                       # Routes, dependencies, middleware
│   ├── core/                      # Config, logging, security
│   ├── database/                  # Models, seeders, repositories
│   ├── ml/                        # ML pipeline (train, predict, adversarial)
│   ├── schemas/                   # Pydantic models (validation)
│   ├── services/                  # Auth, MFA, and user services
│   ├── utils/                     # Enums, shared helpers
│   ├── tests/                     # Pytest-based unit tests
│   ├── alembic/                   # Migration scripts
│   ├── scripts/                   # Setup scripts (DB, etc.)
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/                      # Next.js dashboard (TypeScript)
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   │   ├── (auth)/            # Authentication (login, MFA, etc.)
│   │   │   ├── (dashboard)/       # Main dashboard pages
│   │   │   ├── (admin)/           # Admin management (roles, users)
│   │   │   └── layout.tsx         # Shared layout
│   │   ├── components/            # Reusable UI components
│   │   ├── contexts/              # Global context providers
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── providers/             # Query & Auth providers
│   │   ├── types/                 # TypeScript definitions
│   │   └── middleware.ts
│   ├── public/                    # Static assets
│   ├── package.json
│   └── next.config.ts
│
├── notebooks/                     # Research and EDA notebooks
├── docs/                          # Documentation (e.g., SETUP.md)
├── scripts/                       # Project-level scripts
├── .github/                       # CI/CD & issue templates
│   └── workflows/ci.yml
├── .pre-commit-config.yaml        # Lint & test automation
├── .secrets.baseline              # detect-secrets baseline
├── docker-compose.yml
└── README.md
```

## Development Workflow

### Code Quality

- Pre-commit hooks: Automatically lint and format Python, TypeScript, and check secrets before commit.

- Pre-push hook: Runs backend pytest tests before allowing a push.

To install hooks:
```bash
pre-commit install --hook-type pre-commit --hook-type pre-push
```

To run all checks manually:
```bash
pre-commit run --all-files
```

## Acknowledgments

Built as part of Bsc. Informatics and Computer Science final-year research project on
Enhancing Robustness of ML-based NIDS Against Adversarial Evasion Attacks using adversarial training
and explainable AI.

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

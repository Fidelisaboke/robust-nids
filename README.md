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
5. [License](#license)

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
* **Testing:** `pytest` (backend) and `jest` or `vitest` (frontend planned)
* **CI/CD:** GitHub Actions (`.github/workflows/ci.yml`)
* **Containerization:** `backend/Dockerfile` (frontend container optional)

## Getting Started

### Prerequisites

* Python **3.12+**
* Node.js **18+**
* PostgreSQL (or Docker)
* Git
* Bash shell (Linux/WSL2 recommended)

### Quick Install

- For detailed instructions, see [`docs/SETUP.md`](docs/SETUP.md).

#### Backend Setup (FastAPI)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Fidelisaboke/robust-nids
   cd robust-nids/backend
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/WSL2/macOS
   # .venv\Scripts\activate   # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -e .[dev]
   ```

4. **Set up environment variables:**

   ```bash
   cp .env.example .env
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
   cd ..
   python -m backend.scripts.seed_database
   ```

8. **Set up the dataset:** Follow the detailed instructions in [
   `docs/SETUP.md`](docs/SETUP.md#data-setup-tii-ssrc-23-dataset).

9. **Start the FastAPI server:**

   ```bash
   cd ..
   uvicorn api.main:app --reload
   ```

   Access the API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Frontend Setup (Next.js + TypeScript)

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
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
├── backend/                 # FastAPI backend
│   ├── api/                 # Routes, schemas, and dependencies
│   ├── core/                # Config, logging, constants
│   ├── database/            # Models, repositories, migrations
│   ├── ml/                  # ML pipeline (train, predict, adversarial)
│   ├── services/            # Business logic
│   ├── scripts/             # Setup utilities
│   └── tests/               # Unit tests
│
├── frontend/                # Next.js + TypeScript web dashboard
│   ├── src/app/             # App Router structure
│   │   ├── (auth)/          # Authentication pages
│   │   ├── (dashboard)/     # Dashboard pages
│   │   └── (admin)/         # Admin tools (users, logs, roles)
│   └── public/              # Static assets
│
├── notebooks/               # Research notebooks (EDA, training, testing)
├── docs/                    # Setup and project documentation
└── .github/                 # CI/CD workflows
```

## Key Endpoints (Backend)

| Endpoint        | Method | Description                       |
|-----------------|--------|-----------------------------------|
| `/nids/predict` | POST   | Run ML inference on incoming data |
| `/nids/train`   | POST   | Perform adversarial training      |
| `/nids/alerts`  | GET    | Retrieve recent detection alerts  |
| `/nids/logs`    | GET    | Fetch system or training logs     |
| `/auth/login`   | POST   | Authenticate user                 |
| `/users/`       | CRUD   | Manage analyst and admin accounts |

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

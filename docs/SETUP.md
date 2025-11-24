# Robust NIDS — Full Setup Guide

This guide walks through the local  setup of the **Robust NIDS** full-stack system, including the **FastAPI backend**, **Next.js frontend**, **dataset**, and **developer tooling**.

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. WSL2 Configuration (Windows Users)](#1-wsl2-configuration-windows-users)
- [2. Backend Setup (FastAPI)](#2-backend-setup-fastapi)
- [3. Frontend Setup (Nextjs--React)](#3-frontend-setup-nextjs--react)
- [4. Environment Variables](#4-environment-variables)
- [5. Database Setup](#5-database-setup)
- [6. Dataset Setup (TII-SSRC-23)](#6-dataset-setup-tii-ssrc-23)
- [7. Developer Tooling (Code Quality & Security)](#7-developer-tooling-code-quality--security)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)


## Prerequisites

Make sure the following are installed on your system (inside **WSL2** if on Windows):

- **Git**
- **Python 3.12+**
- **Node.js 20+** and **npm** (or **pnpm**)
- **PostgreSQL 12+**
- **WSL2** (Windows only)
- **Kaggle API credentials** (optional for dataset download)
- [**uv** package manager](https://docs.astral.sh/uv/getting-started/installation/)
- (Optional) **Docker** if containerizing the app later

## 1. WSL2 Configuration (Windows Users)

For optimal performance, run everything inside **WSL2 Ubuntu**.

### Steps

1. **Install WSL2:**
   [Microsoft’s official guide →](https://learn.microsoft.com/en-us/windows/wsl/install)

2. **Clone inside WSL2 (not `/mnt/c/`):**
   ```bash
   cd ~
   mkdir projects && cd projects
   git clone https://github.com/Fidelisaboke/robust-nids.git
   cd robust-nids
   ```

3. *(Optional)* Configure `.wslconfig` limits:

   ```ini
   [wsl2]
   memory=12GB
   processors=6
   ```

## 2. Backend Setup (FastAPI)

### 2.1 Create Virtual Environment

```bash
cd backend
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 2.2 Install Dependencies

```bash
uv pip install --upgrade pip
uv sync
```

### 2.3 Configure Environment

```bash
cp .env.example .env
```

### 2.4 Set Up Database

```bash
./scripts/setup_db.sh
```

### 2.5 Run Alembic Migrations

```bash
alembic upgrade head
```

### 2.6 Seed Database

```bash
python database/seed.py
```

### 2.7 Start the Development Server

```bash
uv run uvicorn api.main:app --reload
```

Visit: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 3. Frontend Setup (Next.js + React)

The frontend uses **Next.js 15**, **TypeScript**, and **ShadCN UI**.

### 3.1 Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
```

### 3.2 Setup Environment

```bash
cp .env.local.example .env.local
```

Then set the backend URL:

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3.3 Run the Frontend

```bash
npm run dev
```

Your app will be live at: [http://localhost:3000](http://localhost:3000)

### 3.4 Folder Overview

```
frontend/
├── components/      # Shared UI components
├── hooks/           # Custom React hooks
├── lib/             # Helpers (API, auth, utils)
├── app/             # Main routes
├── styles/          # Global styles
└── types/           # TypeScript definitions
```

## 4. Environment Variables

### Backend (`backend/.env`)

```bash
cp .env.example .env
```

Example values:

```
DATABASE_URL=postgresql://nids_user:password@localhost:5432/nids_db
JWT_SECRET_KEY=your_secret_key
JWT_REFRESH_SECRET_KEY=your_refresh_secret
```

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```
## Database Setup

### 5.1 PostgreSQL

**Ubuntu:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**

```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
→ [Download PostgreSQL](https://www.postgresql.org/download/windows/)

### Manual Setup (if script fails)

```sql
CREATE DATABASE nids_db;
CREATE USER nids_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nids_db TO nids_user;
```

Test:

```bash
psql -h localhost -U nids_user -d nids_db -c "SELECT version();"
```

### 5.1 Redis Setup

**Ubuntu:**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

**macOS:**

```bash
brew install redis
brew services start redis
```

**Windows:**
→ [Download Redis for Windows](https://github.com/microsoftarchive/redis/releases)

### Configuration

Default configuration is sufficient for development. For custom settings, edit `/etc/redis/redis.conf` (Ubuntu) or use the Redis Desktop Manager.

### Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Environment Variable Example (backend/.env)

```
REDIS_URL=redis://localhost:6379/0
```

---

## 6. Dataset Setup (TII-SSRC-23)

> ⚠️ The dataset is large (~30 GB) and **not versioned in Git**.

### Option 1 — Manual Download (Recommended)

1. Download `data.csv` from the official Kaggle page.
2. Place it under:

   ```
   data/raw/data.csv
   ```

### Option 2 — Automated Download

Requires Kaggle API setup:

```bash
python scripts/download_data.py
```

## 7. Developer Tooling (Code Quality & Security)

### 7.1 Enable Pre-commit Hooks

```bash
pre-commit install
```

Run checks manually:

```bash
pre-commit run --all-files
```

### 7.2 Scan for Secrets

Create a baseline:

```bash
detect-secrets scan > .secrets.baseline
```

Audit:

```bash
detect-secrets audit .secrets.baseline
```

- Commit `.secrets.baseline` to version control.

### 7.3 Run Linters & Formatters

**Python (backend):**

```bash
ruff check . --fix
```

**Frontend (Prettier):**

```bash
npx prettier . --write
```

## Next Steps

1. **Start backend:**

   ```bash
   # In backend/
   uv run uvicorn api.main:app --reload
   ```

2. **Start frontend:**

   ```bash
   # In frontend/
   npm run dev
   ```

3. **Access app:**

   * Frontend → [http://localhost:3000](http://localhost:3000)
   * API Docs → [http://localhost:8000/docs](http://localhost:8000/docs)


## Development Workflow

| Step | Action               | Command                                   |
| ---- | -------------------- | ----------------------------------------- |
| 1    | Start PostgreSQL     | `sudo service postgresql start`           |
| 2    | Run FastAPI backend  | `uv run uvicorn api.main:app --reload`    |
| 3    | Run Next.js frontend | `npm run dev`                             |
| 4    | Run code checks      | `pre-commit run --all-files`              |
| 5    | Scan for secrets     | `detect-secrets scan > .secrets.baseline` |

## Troubleshooting

**Backend not connecting:**
→ Verify `.env` `DATABASE_URL` and ensure PostgreSQL is running.

**Frontend fetch errors:**
→ Check `NEXT_PUBLIC_API_URL` and CORS settings.

**Dataset errors:**
→ Confirm CSV path `data/raw/data.csv` exists.

📘 *Maintainer Notes:*

* CI/CD is configured via **GitHub Actions** (`.github/workflows/ci.yml`).
* Secrets scanning runs automatically in PRs.
* Formatters and type checks are enforced locally and in CI.

**You’re all set!**
Run both servers and start exploring your full-stack, ML-powered **Robust NIDS** system.

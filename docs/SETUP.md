# Setup Guide

This guide walks through the complete setup process for the **Robust NIDS** full-stack system — including the **FastAPI
backend**, **Next.js frontend**, and **dataset configuration**.

## Table of Contents

* [Prerequisites](#prerequisites)
* [1. WSL2 Configuration (Windows Users)](#1-wsl2-configuration-windows-users)
* [2. Backend Setup (FastAPI)](#2-backend-setup-fastapi)
* [3. Frontend Setup (Nextjs--React)](#3-frontend-setup-nextjs--react)
* [4. Environment Variables](#4-environment-variables)
* [5. PostgreSQL Setup](#5-postgresql-setup)
* [6. Dataset Setup (TII-SSRC-23)](#6-dataset-setup-tii-ssrc-23)
* [Next Steps](#next-steps)

## Prerequisites

Ensure the following are installed on your system (preferably inside WSL2 for Windows users):

* **Git**
* **Python 3.9+**
* **Node.js 20+** and **npm** (or **pnpm**)
* **PostgreSQL 12+**
* **WSL2** (Windows only)
* **Kaggle API credentials** (optional for dataset download)

## 1. WSL2 Configuration (Windows Users)

For optimal performance and compatibility, run both backend and frontend within **WSL2** (Ubuntu recommended).

### Steps

1. **Install WSL2:**
   Follow the [official Microsoft guide](https://learn.microsoft.com/en-us/windows/wsl/install).

2. **Clone repository inside WSL2:**
   ```bash
   cd ~
   mkdir projects && cd projects
   git clone https://github.com/Fidelisaboke/robust-nids.git
   cd robust-nids
   ```

3. **Avoid working inside `/mnt/c/`**, which causes file-sync issues.

4. **Limit resources (optional):**
   Create `C:\Users\<YourUsername>\.wslconfig` and configure:

   ```ini
   [wsl2]
   memory=12GB
   processors=6
   ```

## 2. Backend Setup (FastAPI)

### 2.1 Create Python Environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # (Linux/macOS)
# or
.venv\Scripts\activate     # (Windows)
```

### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -e .[dev]
```

### 2.3 Run Development Server

```bash
uvicorn api.main:app --reload
```

### 2.4 Verify

Visit **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** to access Swagger UI and test the API routes.

## 3. Frontend Setup (Next.js + React)

The frontend uses **Next.js 15**, **TypeScript**, and **ShadCN UI**.

### 3.1 Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
```

### 3.2 Environment Variables

Copy and edit the environment example:

```bash
cp .env.example .env.local
```

Set the API base URL (for example):

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 3.3 Run Development Server

```bash
npm run dev
```

Your app should now be live at **[http://localhost:3000](http://localhost:3000)**

### 3.4 Folder Overview

```
frontend/
├── components/      # Shared UI components
├── hooks/           # Custom React hooks
├── lib/             # Helper functions (API, auth, utils)
├── pages/ or app/   # Main routes
├── styles/          # Global styles
└── types/           # TypeScript definitions
```

## 4. Environment Variables

Both backend and frontend rely on `.env` files.

### 4.1 Backend (`backend/.env`)

```bash
cp .env.example .env
```

Then configure values such as:

```
DATABASE_URL=postgresql://nids_user:password@localhost:5432/nids_db
JWT_SECRET_KEY=your_secret_key
JWT_REFRESH_SECRET_KEY=your_refresh_secret
```

### 4.2 Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 5. PostgreSQL Setup

### 5.1 Installation

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (Homebrew):**

```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)

### 5.2 Database Creation

Run the helper script:

```bash
./scripts/setup_db.sh
```

Or manually:

```sql
CREATE DATABASE nids_db;
CREATE USER nids_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nids_db TO nids_user;
```

Verify connection:

```bash
psql -h localhost -U nids_user -d nids_db -c "SELECT version();"
```

## 6. Dataset Setup (TII-SSRC-23)

The TII-SSRC-23 dataset is not tracked in Git due to its size.

### Option 1: Manual Download (Recommended)

1. Download `data.csv` from the official Kaggle source.
2. Place it in:

   ```
   data/raw/data.csv
   ```

### Option 2: Scripted Download

You can automatically fetch and unpack the dataset (requires Kaggle API setup):

```bash
python scripts/download_data.py
```

*(Note: this may take hours depending on bandwidth; ~30 GB total size.)*

## Next Steps

After setup:

1. **Start backend:**

   ```bash
   # Should be at project root
   uvicorn api.main:app --reload
   ```

2. **Start frontend:**

   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the app:**

    * Frontend: [http://localhost:3000](http://localhost:3000)
    * API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Login or register:**
   Default admin credentials are defined in your `.env` or seed script.

## Recommended Development Workflow

| Step | Description                                                    |
|------|----------------------------------------------------------------|
| 1    | Run PostgreSQL locally (`sudo service postgresql start`)       |
| 2    | Start FastAPI backend (`uvicorn api.main:app --reload`)        |
| 3    | Launch frontend (`npm run dev`)                                |
| 4    | View logs and alerts via `/nids/logs` and `/nids/alerts`       |
| 5    | Use `scripts/` for seeding, dataset management, and migrations |

## Troubleshooting

**Backend not connecting to DB:**
→ Check `.env` `DATABASE_URL` and ensure PostgreSQL is running.

**Frontend fetch errors:**
→ Verify `NEXT_PUBLIC_API_URL` is reachable and CORS is configured in FastAPI.

**Dataset errors:**
→ Ensure CSV exists at `data/raw/data.csv` and paths are correct in preprocessing scripts.


# Setup Guide

This guide walks through the complete setup process for the development environment.

## Table of Contents
*   [Prerequisites](#prerequisites)
*   [1. WSL Configuration](#1-wsl2-configuration-windows-users)
*   [2. Python Environment Setup](#2-python-environment-setup)
*   [3. Environment Variables](#3-environment-variables)
*   [4. PostgreSQL Setup](#4-postgresql-setup)
*   [5. Dataset Setup](#5-dataset-setup-tii-ssrc-23-dataset)
*   [Next Steps](#next-steps)

## Prerequisites

*   **Git**
*   **Python 3.9+** (Ensure this is installed on your WSL2 distribution, not just Windows)
*   **WSL2** (Windows users only. Already installed and updated.)
*   **PostgreSQL 12** or higher
*   **psql** command-line tool available
*   **Access to the TII-SSRC-23 Dataset** (Ensure you have the download link or credentials ready.)

## 1. WSL2 Configuration (Windows Users)

For optimal performance on Windows, it is strongly recommended to use WSL2.

**Key Configuration:**
1.  **Install WSL2:** Follow the [official Microsoft guide](https://learn.microsoft.com/en-us/windows/wsl/install).
2.  **Clone and work inside WSL2:** Do not work on files in the `/mnt/c/` mount. Clone the repository inside your WSL2
3. home directory (e.g., `~/projects/robust-nids`).
    *   **Important:** Ensure Python 3.9+ is installed *within* your WSL2 distribution (e.g., Ubuntu). You can check
with `python3 --version`.
4. **Resource Management (Optional):** To prevent WSL2 from consuming all your RAM, create a `.wslconfig` file in your
Windows user directory (`C:\Users\<YourUsername>`):
    ```ini
    [wsl2]
    memory=12GB
    processors=6
    ```

## 2. Python Environment Setup

It is crucial to use an isolated Python environment to manage dependencies.

1.  **Create a virtual environment:**
    ```bash
    # Create the environment in a directory named '.venv'
    python -m venv .venv
    ```

2.  **Activate the virtual environment:**
    ```bash
    # On Linux, WSL2, or macOS:
    source .venv/bin/activate
    # On Windows:
    .venv\Scripts\activate
    ```

3.  **Upgrade pip and install core dependencies:**
    ```bash
    pip install --upgrade pip

    # Install required dependencies
    pip install -e .

    # Alternatively, to install optional dev tools
    pip install -e .[dev]
    ```

4.  **Verify the installation:** Run a quick test to ensure the core scientific libraries can be imported without errors.
    ```bash
    python -c "import pandas; import sklearn; print('All core libraries imported successfully!')"
    ```

## 3. Environment Variables
- To set up your environment, you'll need to set some secret credentials.
- This can be done by creating the environment file (`.env`):
    ```bash
    cp .env.example .env
    ```
- Edit the `.env` file with your credentials.

## 4. PostgreSQL Setup

### PostgreSQL Installation
- If you do not have PostgreSQL, ensure you have it installed for your OS:

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

### DB Setup Script
- **Run the setup script:** This provides an interactive shell for setting up the database instance, making it easier to set up quickly.
   ```bash
   ./scripts/setup_db.sh
   ```

### Manual Setup (Alternative)

If you prefer to set up PostgreSQL manually:

1. **Connect to PostgreSQL as admin**
   ```bash
   sudo -u postgres psql
   ```

2. **Create database and user**
   ```sql
   CREATE DATABASE nids_db;
   CREATE USER nids_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE nids_db TO nids_user;
   ```

3. **Set up schema permissions**
   ```sql
   \c nids_db
   REVOKE ALL ON SCHEMA public FROM PUBLIC;
   GRANT USAGE ON SCHEMA public TO nids_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nids_user;
   ```

### Verification

After setup, verify the database connection:

```bash
# Test connection as application user
psql -h localhost -p 5432 -U nids_user -d nids_db -c "SELECT version();"
```

### Troubleshooting
1. **Connection refused**
   - Ensure PostgreSQL is running: `sudo service postgresql start`
   - Check if PostgreSQL is listening on the correct port

2. **Authentication failed**
   - Verify your password in the `.env` file
   - Check pg_hba.conf for authentication method

3. **Permission denied**
   - Ensure the admin user has sufficient privileges

### Security Notes

- Change default passwords in production
- Restrict database access to specific IPs in production
- Regularly backup your database
- Consider using SSL for database connections in production

For detailed configuration, refer to the [PostgreSQL documentation](https://www.postgresql.org/docs/).


## 5. Dataset Setup (TII-SSRC-23 Dataset)

The TII-SSRC-23 dataset is not stored in Git.

**Option 1: Manual Download (Recommended)**

1.  Download only the CSV dataset (`csv/data.csv`) from the official source on Kaggle (about 5 GB).
2.  Place the raw data files in the `data/raw/` directory.

**Option 2: Download via Script**

A helper script is provided to download the data from a predefined source. Use this if you'd like to
download the entire dataset, including PCAP files. (Warning: the ZIP file will be very big, approx. 30 GB)
- **Note:**: This requires a [Kaggle API token.](https://www.kaggle.com/code/webdevbadger/comprehensive-kaggle-workspace-with-vs-code-wsl)
```bash
# Run the download script
python scripts/download_data.py
```

## Next Steps

After setup:

1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. The first time you run the app, it will create the necessary tables

3. Log in with the default admin credentials (check your app documentation)

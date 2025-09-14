
# Setup Guide

This guide walks through the complete setup process for the development environment.

## Prerequisites

*   **Git**
*   **Python 3.9+** (Ensure this is installed on your WSL2 distribution, not just Windows)
*   **WSL2** (Windows users only. Already installed and updated.)
*   **Access to the TII-SSRC-23 Dataset** (Ensure you have the download link or credentials ready.)

## 1. WSL2 Configuration (Windows Users)

For optimal performance on Windows, it is strongly recommended to use WSL2.

**Key Configuration:**
1.  **Install WSL2:** Follow the [official Microsoft guide](https://learn.microsoft.com/en-us/windows/wsl/install).
2.  **Clone and work inside WSL2:** Do not work on files in the `/mnt/c/` mount. Clone the repository inside your WSL2 
3. home directory (e.g., `~/projects/robust-nids`).
    *   **Important:** Ensure Python 3.9+ is installed *within* your WSL2 distribution (e.g., Ubuntu). You can check 
with `python3 --version`.
3.  **Resource Management (Optional):** To prevent WSL2 from consuming all your RAM, create a `.wslconfig` file in your 
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
    pip install -r requirements.txt
    ```

4.  **Verify the installation:** Run a quick test to ensure the core scientific libraries can be imported without errors.
    ```bash
    python -c "import pandas; import sklearn; print('All core libraries imported successfully!')"
    ```

## 3. Data Setup (TII-SSRC-23 Dataset)

The 30 GB TII-SSRC-23 dataset is not stored in Git.

**Option 1: Manual Download**

1.  Download the dataset from the official source.
2.  Place the raw data files in the `data/raw/` directory.

**Option 2: Download via Script (Recommended)**

A helper script is provided to download the data from a predefined source.
- **Note:**: This requires a [Kaggle API token.](https://www.kaggle.com/code/webdevbadger/comprehensive-kaggle-workspace-with-vs-code-wsl)
```bash
# Run the download script
python scripts/download_data.py
```
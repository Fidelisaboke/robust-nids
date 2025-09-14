"""
Script to download the TII-SSRC-23 dataset from Kaggle.

This script uses the Kaggle API to download the dataset and stores it in the
project's `data/raw/` directory. The dataset is approximately 30 GB in size.

Prerequisites:
1. A Kaggle account and API token (kaggle.json).
2. The Kaggle Python package installed (`pip install kaggle`).
3. You must have accepted the dataset rules on the Kaggle website:
   https://www.kaggle.com/datasets/daniaherzalla/tii-ssrc-23

Usage:
    python scripts/download_data.py
"""

import os
import sys
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

# Configuration
DATASET_NAME = "daniaherzalla/tii-ssrc-23"
DATASET_URL = "https://www.kaggle.com/datasets/daniaherzalla/tii-ssrc-23"
TARGET_DIR = Path("./data/raw")


def main():
    """Main function to execute the dataset download process."""
    # Ensure the target directory exists
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target directory ensured: {TARGET_DIR.absolute()}")

    # Initialize the Kaggle API
    api = KaggleApi()

    try:
        # Attempt to authenticate using the kaggle.json file
        api.authenticate()
        print("SUCCESS: Authenticated with the Kaggle API.")
    except Exception as e:
        print(f"ERROR: Kaggle API authentication failed: {e}")
        print("\nTroubleshooting checklist:")
        print("1. You have a Kaggle account and are logged in.")
        print("2. You have created an API token (kaggle.json).")
        print(
            "3. The kaggle.json file is placed in ~/.kaggle/ (Linux/WSL/Mac) or C:\\Users\\<username>\\.kaggle\\ (Windows)."
        )
        print("4. You have accepted the dataset rules on the Kaggle website.")
        print(f"   Visit: {DATASET_URL}")
        sys.exit(1)

    print(f"Preparing to download dataset: '{DATASET_NAME}'")
    print(
        "NOTE: This dataset is approximately 30 GB. The download may take a significant amount of time."
    )
    print(f"Files will be saved to: {TARGET_DIR.absolute()}")
    print("-" * 50)

    try:
        # Download the dataset
        api.dataset_download_files(
            dataset=DATASET_NAME, path=TARGET_DIR, unzip=True, quiet=False, force=False
        )
        print("SUCCESS: Download and extraction completed successfully.")
        print(f"Please check the contents of: {TARGET_DIR.absolute()}")

    except Exception as e:
        print(f"ERROR: An error occurred during download: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

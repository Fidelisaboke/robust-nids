# Adversarially Robust Network Intrusion Detection System (NIDS)

[![python-3.12](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![Python Code Quality and Tests](https://github.com/Fidelisaboke/robust-nids/actions/workflows/test.yml/badge.svg)](https://github.com/Fidelisaboke/robust-nids/actions/workflows/test.yml)

## Project Overview
A machine learning-based Network Intrusion Detection System designed to be resilient against adversarial evasion attacks. 
Features a dashboard for analysts to monitor traffic, review alerts, and provide feedback for continuous improvement.

**Key Features:**
*   **Adversarial Training:** Models are hardened against evasion attempts using state-of-the-art attacks from the 
Adversarial Robustness Toolbox (ART).
*   **Dual Detection Strategy:** Combines a powerful XGBoost classifier for known attacks with an Autoencoder for 
* detecting novel anomalies.
*   **Analyst-in-the-Loop:** Includes a feedback mechanism for cybersecurity operators to label false 
* positives/negatives, enabling iterative model refinement.
*   **Explainable AI:** Integrates LIME to provide explanations for model predictions, building trust and understanding.
*   **Live Monitoring Dashboard:** A Streamlit-based dashboard for real-time traffic analysis and alert visualization.

## Table of Contents

1.  [Tech Stack](#tech-stack)
2.  [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Setup Instructions](#setup-instructions)
3.  [Basic Usage](#basic-usage)
4.  [Project Structure](#project-structure)
5.  [License](#license)

## Tech Stack
### Machine Learning & Data Processing
- Pandas
- Scikit-learn
- XGBoost
- TensorFlow
- Adversarial Robustness Toolbox (ART)

### Dashboard
- Streamlit

### Development & Operations
- Git
- GitHub Actions
- MinIO
- pytest
- Black
- Flake8

## Getting Started

### Prerequisites

- Python 3.12+
- Git

### Quick Install

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/Fidelisaboke/robust-nids
    cd robust-nids
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/WSL2/macOS
    # .venv\Scripts\activate  # Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Set up the dataset:** Follow the detailed instructions in [`docs/SETUP.md`](docs/SETUP.md#data-setup-tii-ssrc-23-dataset).

## Basic Usage

1.  **Start the Streamlit Dashboard:**
    Navigate to the project root and run:
    ```bash
    streamlit run app.py
    ```
    The application will start and be available in your web browser at `http://localhost:8501`.

2.  **Log In:**
    Use the credentials configured in `config.yaml` to log in via the Streamlit-Authenticator interface.

3.  **Using the Dashboard:**
    *   **Dashboard Tab:** View high-level system metrics and live traffic overview.
    *   **Monitoring Tab:** See a simulated feed of network traffic alerts. Provide feedback on false positives/negatives.
    *   **Analytics Tab:** Explore model performance metrics (F1-Score, AUC-ROC curves) and explanations for predictions using LIME.
    *   **Playground Tab:** Input feature values manually to get a real-time model prediction and explanation.

4.  **Running Tests:**
    To ensure code quality, run the test suite with pytest:
    ```bash
    pytest -v tests/
    ```

## Project Structure

```
├── .github/workflows          # GitHub Actions CI/CD workflows
├── data/                      # IGNORED BY GIT - Raw and processed data
├── docs/                      # Project documentation and guides
├── models/                    # IGNORED BY GIT - Serialized trained models
├── notebooks/                 # Jupyter notebooks for EDA and prototyping
├── scripts/                   # Utility scripts (e.g., data download)
├── src/                       # Main source code package
│   ├── data/                  # Code for data loading and preprocessing
│   ├── features/              # Code for feature engineering & adversarial generation
│   ├── models/                # Code for training, prediction, and evaluation
│   └── visualization/         # Code for generating plots and charts
├── tests/                     # Unit tests
├── app.py                     # Main Streamlit application entry point
├── requirements.txt           # Project dependencies
└── README.md                  # This file
```

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

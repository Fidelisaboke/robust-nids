
# Robust-NIDS: Technical Report

## 1. Executive Summary

Robust-NIDS is a modular network intrusion detection system (NIDS) leveraging machine learning and adversarial training to detect cyber threats. The project includes:
- Data science notebooks for exploratory analysis, sampling, preprocessing, baseline and adversarial model training.
- Backend (FastAPI) and frontend (Next.js) for deployment and reporting.
- Support for binary, multiclass, and anomaly detection, with adversarial robustness evaluation.

## 2. Approach

### 2.1 Data Exploration & Sampling

- **Dataset**: TII-SSRC-23 (Herzalla et. al, 2023)
    - Two classes (Benign, Malicious), 8 traffic types, and 32 subtypes
    - Approx. 8.6 million records

- **Stratified Sampling:**
  - Stratified sampling is applied for binary and multiclass targets, preserving the proportion of each class in train, validation, and test sets.
  - 200,000 traffic flows picked.
  - For anomaly detection, benign and malicious samples are separated, with benign data used for unsupervised model training and mixed sets for evaluation.

### 2.2 Preprocessing

- **Data Cleaning:**
  - Raw network flow data is loaded and columns irrelevant to modeling (e.g., identifiers, timestamps) are dropped.
  - Missing values are imputed using median values for numerical features.
  - Outliers are handled by feature selection and scaling.
- **Feature Engineering:**
  - Features are engineered to capture protocol, statistical, and temporal properties of flows.
  - Categorical features (e.g., protocol types) are one-hot encoded.
  - Numerical features are scaled using MinMaxScaler to [0, 1] range.
- **Train/Test Splitting:**
  - Data is split into train (70%), validation (15%), and test (15%) sets using stratified sampling to maintain class proportions.
  - For unsupervised models, pure benign data is used for training, while validation and test sets are mixed (benign + malicious) to evaluate anomaly detection.
- **Preprocessing Pipelines:**
  - Scikit-learn pipelines are constructed for imputation, scaling, and feature selection (VarianceThreshold, SelectKBest).
  - Pipelines are fitted only on training data and applied identically to validation and test sets to prevent data leakage.


### 2.3 Baseline Model Training
Multiple supervised and unsupervised models are trained and compared:

- **XGBoost (Binary & Multiclass):**
  - Tree-based gradient boosting classifier.
  - Key hyperparameters:
    - `n_estimators`: 100 (binary), 150 (multiclass)
    - `scale_pos_weight`: Handles class imbalance
    - `eval_metric`: `'logloss'` (binary), `'mlogloss'` (multiclass)
    - `random_state`: 42 (reproducibility)
    - Multiclass-specific:
      - `objective`: `'multi:softprob'`
      - `tree_method`: `'hist'` (efficient training)

- **Random Forest (Binary & Multiclass):**
  - Ensemble of decision trees with bagging.
  - Key hyperparameters:
    - `n_estimators`: 100 (binary), 150 (multiclass)
    - `class_weight`: `'balanced'` (binary)
    - `random_state`: 42 (reproducibility)
    - `n_jobs`: -1 (parallelism)

- **Autoencoder (Anomaly Detection):**
  - Deep neural network trained to reconstruct benign traffic.
  - Architecture:
    - Input layer: size = number of features
    - Encoder: Dense(128, relu) → BatchNorm → Dropout(0.2) → Dense(64, relu) → Dense(32, relu, L1 regularization)
    - Decoder: Dense(64, relu) → Dense(128, relu) → BatchNorm → Output: Dense(input_dim, sigmoid)
  - Trained with `Adam` optimizer (lr=0.001), `loss='mae'`, `batch_size=64`, up to 100 epochs, with early stopping and learning rate reduction on plateau.

- **Other Models:**
  - Logistic Regression (with `class_weight='balanced'`)
  - Isolation Forest, One-Class SVM, Local Outlier Factor for anomaly detection.

Model selection is based on validation F1-score and ROC-AUC (`04_baseline_model_training.ipynb`).

### 2.4 Adversarial Training

- A differentiable surrogate model (Keras MLP) is trained to generate adversarial samples.
- Targeted FGSM and PGD attacks are implemented:
    - **FGSM:**
    ```math
    x_{adv} = x - \epsilon \cdot \text{sign}(\nabla_x J(\theta, x, y))
    ```


    - **PGD:**
    ```math
    x_{adv}^{t+1} = \text{clip}_{x, \epsilon}\left( 
    x_{adv}^t - \alpha \cdot \text{sign}(\nabla_x J(\theta, x_{adv}^t, y)) 
    \right)
    ```
- Adversarial samples (malicious flows perturbed to evade detection) are generated for multiple epsilon values.
- Robust models are trained by augmenting the training set with adversarial samples (`05_adversarial_model_training.ipynb`).

### 2.5 Evaluation Metrics

- **Classification**: Accuracy, Precision, Recall, F1-score, ROC-AUC.
- **Robustness**: Adversarial accuracy, Attack Success Rate (ASR).

## 3. Results

### 3.1 Model Performance Comparison

#### 3.1.1 Binary Classification (Validation)

| Model               | F1 (Malicious) | Precision (Malicious) | Recall (Malicious) | ROC-AUC   |
|---------------------|----------------|-----------------------|--------------------|-----------|
| Logistic Regression | 0.9887         | 0.9958                | 0.9817             | 0.9922    |
| Random Forest       | 0.9993         | 0.9992                | 0.9993             | 0.9998    |
| XGBoost             | 0.9993         | 0.9997                | 0.9989             | 0.99997   |

#### 3.1.2 Multiclass Classification (Validation)

| Model         | Accuracy  | Precision | Recall   | F1-score |
|---------------|-----------|-----------|----------|----------|
| XGBoost       | 0.9956    | 0.9302    | 0.9251   | 0.9278   |
| Random Forest | 0.9941    | 0.9217    | 0.9173   | 0.9195   |

#### 3.1.3 Unsupervised / Anomaly Detection (Validation)

| Model                | F1 (Malicious) | Precision (Malicious) | Recall (Malicious) | ROC-AUC   |
|----------------------|----------------|-----------------------|--------------------|-----------|
| Isolation Forest     | 0.0194         | 0.9272                | 0.0098             | 0.9321    |
| One-Class SVM        | 0.6073         | 0.9976                | 0.4365             | 0.7148    |
| Local Outlier Factor | 0.5273         | 0.9971                | 0.3584             | 0.9522    |
| Autoencoder          | 0.9939         | 0.9878                | 0.99997            | 0.9782    |

### 3.2 Adversarial Robustness Comparison

| Model            | Scenario         | Accuracy | Precision | Recall   | F1-score | ASR    |
|------------------|-----------------|----------|-----------|----------|----------|--------|
| Baseline XGBoost | Clean            | 0.9988   | 0.9996    | 0.9990   | 0.9993   |   -    |
| Baseline XGBoost | FGSM (ε=0.2)     | 0.0382   | 0.9904    | 0.0382   | 0.0735   | 0.9618 |
| Baseline XGBoost | PGD (ε=0.2)      | 0.0618   | 0.9941    | 0.0618   | 0.1163   | 0.9382 |
| Robust XGBoost   | Clean            | 0.9987   | 0.9992    | 0.9994   | 0.9993   |   -    |
| Robust XGBoost   | FGSM (ε=0.2)     | 1.0000   | 0.9992    | 1.0000   | 0.9996   | 0.0000 |
| Robust XGBoost   | PGD (ε=0.2)      | 0.9362   | 0.9992    | 0.9362   | 0.9677   | 0.0638 |

### 3.3 Key Findings

- Baseline models are highly vulnerable to adversarial attacks (FGSM, PGD).
- Adversarial training restores high accuracy and robustness under attack.
- Mixed test sets (benign + adversarial) confirm robust models maintain detection rates.

## 4. Challenges

- Severe class imbalance TII-SSRC-23.
- Transferability of adversarial samples between surrogate and baseline models.
- Hyperparameter tuning for adversarial attacks and robust training.
- Ensuring reproducibility and scalability for large datasets.

## 5. Conclusion

Robust-NIDS demonstrates that adversarial training is essential for resilient intrusion detection. The workflow—from sampling and preprocessing to robust model training and evaluation—ensures high accuracy and robustness against sophisticated evasion techniques. The modular notebooks and codebase provide a reproducible pipeline for future research and deployment.

---

*For full details, see the notebooks in `/notebooks`.*

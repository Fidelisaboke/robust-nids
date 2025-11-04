import os

import joblib
import numpy as np
from xgboost import XGBClassifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), "artifacts")


class ModelBundle:
    """ModelBundle loads and holds ML models and related artifacts."""

    def __init__(self):
        self.binary_scaler = None
        self.multiclass_scaler = None
        self.label_encoder = None
        self.binary_classifier = None
        self.multi_classifier = None
        self.meta = {}

    def load_all(self, model_dir: str = MODEL_DIR):
        """Loads all models and artifacts.

        Args:
            model_dir (str, optional): The directory to load models from. Defaults to MODEL_DIR.
        """
        binary_scaler_path = os.path.join(model_dir, "binary_scaler.pkl")
        if os.path.exists(binary_scaler_path):
            self.binary_scaler = joblib.load(binary_scaler_path)

        multiclass_scaler_path = os.path.join(model_dir, "multiclass_scaler.pkl")
        if os.path.exists(multiclass_scaler_path):
            self.multiclass_scaler = joblib.load(multiclass_scaler_path)

        le_path = os.path.join(model_dir, "label_encoder.pkl")
        if os.path.exists(le_path):
            self.label_encoder = joblib.load(le_path)

        binary_path = os.path.join(model_dir, "binary_classifier.json")
        if os.path.exists(binary_path):
            xgb_binary = XGBClassifier()
            xgb_binary.load_model(binary_path)
            self.binary_classifier = xgb_binary

        multi_path = os.path.join(model_dir, "multiclass_classifier.json")
        if os.path.exists(multi_path):
            xgb_multi = XGBClassifier()
            xgb_multi.load_model(multi_path)
            self.multi_classifier = xgb_multi

        # Metadata
        self.meta = {
            "loaded": {
                "binary_scaler": bool(self.binary_scaler),
                "multiclass_scaler": bool(self.multiclass_scaler),
                "label_encoder": bool(self.label_encoder),
                "binary_classifier": bool(self.binary_classifier),
                "multi_classifier": bool(self.multi_classifier),
            }
        }

    def transform(self, X: np.ndarray | list, multiclass: bool = False):
        """Transforms the input features.

        Args:
            X (np.ndarray or list): The input features to transform.

        Returns:
            np.ndarray: The transformed features.
        """
        if not multiclass:
            scaler = self.binary_scaler
        else:
            scaler = self.multiclass_scaler
        if scaler is None:
            return X

        X_np = np.asarray(X)
        if X_np.ndim == 1:
            X_np = X_np.reshape(1, -1)
        return scaler.transform(X_np)

    def predict_binary(self, X_scaled: np.ndarray):
        """Performs binary classification on the input data.

        Args:
            X_scaled (np.ndarray): The scaled input features.

        Raises:
            RuntimeError: If the binary classifier is not loaded.

        Returns:
            tuple: A tuple containing the predicted class and probabilities.
        """
        if self.binary_classifier is None:
            raise RuntimeError("Binary model not loaded")

        pred = self.binary_classifier.predict(X_scaled)
        pred_probas = (
            self.binary_classifier.predict_proba(X_scaled)
            if hasattr(self.binary_classifier, "predict_proba")
            else None
        )
        return pred, pred_probas

    def predict_multiclass(self, X_scaled: np.ndarray):
        """Performs multiclass classification on the input data.

        Args:
            X_scaled (np.ndarray): The scaled input features.

        Raises:
            RuntimeError: If the multiclass classifier is not loaded.

        Returns:
            tuple: A tuple containing the predicted class and probabilities.
        """
        if self.multi_classifier is None:
            raise RuntimeError("Multiclass model not loaded")
        pred = self.multi_classifier.predict(X_scaled)
        pred_probas = (
            self.multi_classifier.predict_proba(X_scaled)
            if hasattr(self.multi_classifier, "predict_proba")
            else None
        )
        return pred, pred_probas


MODEL_BUNDLE = ModelBundle()

import logging
import os

import joblib
import shap
import tensorflow as tf
from xgboost import XGBClassifier

# Suppress TF warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

logger = logging.getLogger("uvicorn.error")
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")


class ModelBundle:
    """Singleton-style bundle to hold all loaded active models."""

    def __init__(self):
        # Binary
        self.binary_model = None
        self.binary_preprocessor = None
        self.binary_explainer = None
        # Multiclass
        self.multiclass_model = None
        self.multiclass_preprocessor = None
        self.label_encoder = None
        # Unsupervised
        self.unsupervised_pipeline = None
        self.autoencoder = None
        self.ae_threshold = 0.0
        # Status
        self.loaded = False
        self.meta = {"status": "not_loaded"}

    def load_all(self, artifacts_dir: str = ARTIFACTS_DIR):
        logger.info(f"Loading ML artifacts from {artifacts_dir}...")
        try:
            # --- 1. Load Binary Model ---
            xgb_bin_path = os.path.join(artifacts_dir, "xgboost_binary.json")
            if os.path.exists(xgb_bin_path):
                logger.info("Loading Binary model as native XGBoost...")
                self.binary_preprocessor = joblib.load(os.path.join(artifacts_dir, "binary_preprocessor.pkl"))
                self.binary_model = XGBClassifier()
                self.binary_model.load_model(xgb_bin_path)
                bin_type = "xgboost_native"
            else:
                logger.info("Loading Binary model as standard Pipeline...")
                self.binary_model = joblib.load(os.path.join(artifacts_dir, "binary_pipeline.pkl"))
                self.binary_preprocessor = None
                bin_type = "sklearn_pipeline"

            # Initialize SHAP explaienr for binary model
            try:
                logger.info("Initializing Binary SHAP explainer...")
                #  Unwrap the actual model from the pipeline or Native JSON
                if self.binary_preprocessor:
                     actual_model = self.binary_model
                else:
                    actual_model = self.binary_model.named_steps['model']
                self.binary_explainer = shap.TreeExplainer(actual_model)
            except Exception as e:
                logger.warning(f"[ERROR]: Could not initialize SHAP explainer: {e}")

            # --- 2. Load Multiclass Model ---
            xgb_multi_path = os.path.join(artifacts_dir, "xgboost_multiclass.json")
            if os.path.exists(xgb_multi_path):
                logger.info("Loading Multiclass model as native XGBoost...")
                self.multiclass_preprocessor = joblib.load(
                    os.path.join(artifacts_dir, "multiclass_preprocessor.pkl")
                )
                self.multiclass_model = XGBClassifier()
                self.multiclass_model.load_model(xgb_multi_path)
                multi_type = "xgboost_native"
            else:
                logger.info("Loading Multiclass model as standard Pipeline...")
                self.multiclass_model = joblib.load(os.path.join(artifacts_dir, "multiclass_pipeline.pkl"))
                self.multiclass_preprocessor = None
                multi_type = "sklearn_pipeline"

            self.label_encoder = joblib.load(os.path.join(artifacts_dir, "label_encoder.pkl"))

            # --- 3. Load Unsupervised Artifacts ---
            self.unsupervised_pipeline = joblib.load(os.path.join(artifacts_dir, "unsupervised_pipeline.pkl"))
            self.autoencoder = tf.keras.models.load_model(
                os.path.join(artifacts_dir, "autoencoder_model.keras")
            )
            with open(os.path.join(artifacts_dir, "ae_threshold.txt"), "r") as f:
                self.ae_threshold = float(f.read().strip())

            self.loaded = True
            self.meta = {
                "status": "loaded",
                "binary_type": bin_type,
                "multiclass_type": multi_type,
                "ae_threshold": self.ae_threshold,
                "classes": self.label_encoder.classes_.tolist() if self.label_encoder else [],
            }
            logger.info("All NIDS models loaded successfully.")

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.loaded = False
            self.meta = {"status": "error", "error": str(e)}

    # --- Helper Methods ---
    def _prepare_input(self, df, preprocessor):
        return preprocessor.transform(df) if preprocessor else df

    def get_binary_prediction(self, df):
        data = self._prepare_input(df, self.binary_preprocessor)
        return self.binary_model.predict(data)[0], self.binary_model.predict_proba(data)[0]

    def get_multiclass_prediction(self, df):
        data = self._prepare_input(df, self.multiclass_preprocessor)
        return self.multiclass_model.predict(data)[0], self.multiclass_model.predict_proba(data)[0]


MODEL_BUNDLE = ModelBundle()

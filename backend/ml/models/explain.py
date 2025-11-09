import numpy as np
import pandas as pd

from ml.models.loader import MODEL_BUNDLE
from ml.models.predict import _prepare_dataframe


def get_pipeline_feature_names(pipeline, input_features):
    """
    Attempts to recover feature names after they've passed through a scikit-learn Pipeline.
    Handles ColumnTransformer and Selectors.
    """
    current_features = input_features

    # If the pipeline has a 'preprocessor' (ColumnTransformer)
    if "preprocessor" in pipeline.named_steps:
        preproc = pipeline.named_steps["preprocessor"]
        try:
            # Modern sklearn (1.0+) supports this if everything is standard
            current_features = preproc.get_feature_names_out()
        except Exception:
            # Fallback: assume it didn't change the number of features if it failed
            pass

    # If the pipeline has a 'selector' (SelectKBest/VarianceThreshold)
    if "selector" in pipeline.named_steps:
        selector = pipeline.named_steps["selector"]
        try:
            # This is the critical step: getting names AFTER selection
            # We need to pass the input names to get the output names
            if hasattr(selector, "get_feature_names_out"):
                current_features = selector.get_feature_names_out(current_features)
            else:
                # Older sklearn fallback
                mask = selector.get_support()
                current_features = np.array(current_features)[mask]
        except Exception as e:
            print(f"Warning: Could not get selector feature names: {e}")

    return current_features


def explain_binary(features: dict, top_n: int = 10) -> dict:
    """
    Generates SHAP local explanations for a single flow.
    """
    bundle = MODEL_BUNDLE
    if not bundle.loaded or not bundle.binary_explainer:
        raise RuntimeError("Explainer not loaded.")

    # 1. Prepare Raw Dataframe to get initial column names
    df_raw = _prepare_dataframe(features)
    raw_col_names = df_raw.columns.tolist()

    # 2. Transform Data for the model
    if bundle.binary_preprocessor:
        # Native XGBoost case
        X_transformed = bundle.binary_preprocessor.transform(df_raw)
        try:
            # Try to get names from the standalone preprocessor pipeline
            feature_names = get_pipeline_feature_names(bundle.binary_preprocessor, raw_col_names)
        except Exception:
            feature_names = [f"Feature {i}" for i in range(X_transformed.shape[1])]
    else:
        # Standard Pipeline case
        pipeline = bundle.binary_model
        # Run through all steps except the final model to get input for SHAP
        X_transformed = df_raw
        for name, step in pipeline.named_steps.items():
            if name == "model":
                break
            X_transformed = step.transform(X_transformed)

        # Recover feature names from the pipeline steps
        try:
            feature_names = get_pipeline_feature_names(pipeline, raw_col_names)
        except Exception:
            feature_names = [f"Feature_{i}" for i in range(X_transformed.shape[1])]

    # 3. Calculate SHAP Values
    shap_vals = bundle.binary_explainer.shap_values(X_transformed)

    # Handle different SHAP output shapes
    if isinstance(shap_vals, list):
        # RandomForest returns [class0, class1], we want Malicious (class1)
        vals = shap_vals[1][0]
    else:
        # XGBoost returns just one array for binary
        vals = shap_vals[0]

    # 4. Map back to readable format
    base_value = bundle.binary_explainer.expected_value
    if isinstance(base_value, np.ndarray):
        base_value = base_value[1] if len(base_value) > 1 else base_value[0]

    contributions = []
    # Ensure we don't go out of bounds if names didn't match output shape perfectly
    safe_range = min(len(feature_names), len(vals))

    for i in range(safe_range):
        # Clean up sklearn's verbose naming (e.g., "num__Flow Duration" -> "Flow Duration")
        raw_name = str(feature_names[i])
        clean_name = raw_name.split("__")[-1] if "__" in raw_name else raw_name

        # Attempt to find the original value for this feature
        # If it was a scaled numerical feature, this tries to grab the unscaled version for display
        original_val = df_raw.get(clean_name, pd.Series([X_transformed[0][i]])).values[0]

        contributions.append({"feature": clean_name, "value": original_val, "shap_value": float(vals[i])})

    # Sort by absolute impact
    contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    return {"base_value": float(base_value), "contributions": contributions[:top_n]}

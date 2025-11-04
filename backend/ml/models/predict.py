from ml.models.loader import MODEL_BUNDLE


def predict_sample_binary(features: list[float]):
    """Run inference on a single feature vector for binary classification."""
    bundle = MODEL_BUNDLE

    if (bundle.binary_classifier or bundle.multi_classifier) is None:
        raise RuntimeError("Model bundle not loaded. Ensure FastAPI lifespan loads it first.")

    # Convert input into a numpy array and scale
    X_scaled = bundle.transform(features)

    # Get binary predictions
    binary_cls, binary_proba = bundle.predict_binary(X_scaled)

    # Decode binary class (0 - Benign, 1 - Malicious)
    binary_label = "Benign" if binary_cls == 0 else "Malicious"

    # Convert numpy array to list
    binary_proba_list = binary_proba.tolist()[0]

    return {
        "binary": binary_label,
        "binary_proba": binary_proba_list,
    }

def predict_sample_multi(features: list[float]):
    """Run inference on a single feature vector for multiclass classification."""
    bundle = MODEL_BUNDLE

    if (bundle.binary_classifier or bundle.multi_classifier) is None:
        raise RuntimeError("Model bundle not loaded. Ensure FastAPI lifespan loads it first.")

    # Convert input into a numpy array and scale
    X_scaled = bundle.transform(features)

    # Get multiclass predictions
    multilabel_cls, multi_proba = bundle.predict_multiclass(X_scaled)

    # Decode multiclass if encoder provided
    if bundle.label_encoder is not None:
        multiclass_label = bundle.label_encoder.inverse_transform(multilabel_cls).tolist()[0]

    # Convert numpy array to list
    multi_proba_list = multi_proba.tolist()[0]

    return {
        "multilabel": multiclass_label,
        "multilabel_proba": multi_proba_list,
    }

from typing import Dict, Union

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Accepts a dictionary of features (key=column name, value=value)."""
    features: Dict[str, Union[float, int, str]] = Field(
        ..., example={"Flow Duration": 156, "Total Fwd Packets": 2, "Protocol": 6}
    )

class BinaryResult(BaseModel):
    label: str
    confidence: float
    is_malicious: bool

class MulticlassResult(BaseModel):
    label: str
    confidence: float
    probabilities: Dict[str, float]

class AnomalyResult(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    threshold: float

class UnifiedPredictionResponse(BaseModel):
    status: str = "success"
    timestamp: str
    binary: BinaryResult
    multiclass: MulticlassResult
    anomaly: AnomalyResult
    threat_level: str
